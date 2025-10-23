import os
import re
import shutil
import asyncio
import subprocess
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import sys

import requests
import yt_dlp
from tqdm import tqdm
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from PIL import Image
from io import BytesIO

# ------------------------------
# App dir, paths, and cookie helpers
# ------------------------------
def get_app_dir():
    """Directory of the frozen executable, else this script's directory."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

APP_DIR = get_app_dir()
COOKIE_PATH = os.path.join(APP_DIR, "soundcloud_cookies.txt")

def resolve_path(path: str) -> str:
    """Resolve relative paths against the app directory."""
    if not path:
        return APP_DIR
    return path if os.path.isabs(path) else os.path.join(APP_DIR, path)

def has_saved_cookie() -> bool:
    try:
        return os.path.isfile(COOKIE_PATH) and os.path.getsize(COOKIE_PATH) > 0
    except Exception:
        return False

def save_cookie_text(text: str) -> None:
    os.makedirs(APP_DIR, exist_ok=True)
    with open(COOKIE_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.strip() + "\n")

def read_cookie_from_clipboard() -> str:
    """Try to read cookie text from the system clipboard."""
    try:
        if sys.platform == "darwin":
            p = subprocess.run(["pbpaste"], capture_output=True, text=True)
            if p.returncode == 0:
                return p.stdout.strip()
        elif os.name == "nt":
            p = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
                capture_output=True, text=True
            )
            if p.returncode == 0:
                return p.stdout.strip()
    except Exception:
        pass
    return ""

def prompt_cookie_paste() -> str:
    """Prompt user to paste Netscape-format cookies.
    Finish by pressing Enter on an empty line, or typing EOF/END/DONE."""
    print("\nPaste your Netscape-format cookies below.")
    print("- It's normal to see a 'pasting with tabs' warning. Confirm the paste.")
    print("- Finish with an empty line (press Enter on a blank line), or type EOF/END/DONE.")
    print("- Tip: Use a browser extension like 'Cookie-Editor' to export in Netscape format.\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        # Handle bracketed paste markers some terminals send
        clean = line.replace("\x1b[200~", "").replace("\x1b[201~", "")
        # End conditions
        up = clean.strip().upper()
        if up in ("EOF", "END", "DONE"):
            break
        if clean.strip() == "" and lines:
            break
        lines.append(clean)
    return "\n".join(lines).strip()

# ------------------------------
# Utilities
# ------------------------------
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def get_bitrate(filepath):
    """Return bitrate in kbps using ffprobe"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=bit_rate", "-of",
             "default=noprint_wrappers=1:nokey=1", filepath],
            capture_output=True, text=True
        )
        return int(result.stdout.strip()) // 1000
    except Exception:
        return 0

def should_retry_with_auth(err: Exception) -> bool:
    """Detect errors that likely need authentication or a different rate bucket."""
    msg = str(err).lower()
    auth_signals = (
        "http error 401",
        "http error 403",
        "login required",
        "sign in",
        "authentication required",
        "private",
        "you must be signed in",
        "not available to you",
        "this resource requires authentication",
        "http error 429",
        "only available for registered users",
    )
    return any(s in msg for s in auth_signals)

def menu():
    config = {
        "playlist_url": "",
        "download_folder": "downloads",          # resolved relative to APP_DIR
        "authenticate": has_saved_cookie(),      # auto-enable if cookie already saved
        "add_artwork": True,
        "min_bitrate": 320,
        "max_workers": 6,
    }

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🎵 SoundCloud Downloader Menu 🎵")
        print("--------------------------------")
        print(f"1. URL (track or playlist): {config['playlist_url'] or '[not set]'}")
        print(f"2. Download folder: {config['download_folder']}  (relative to: {APP_DIR})")
        print(f"3. Authenticate: {'Yes' if config['authenticate'] else 'No'}  | Saved cookie: {'Yes' if has_saved_cookie() else 'No'}")
        print(f"4. Embed artwork: {'Yes' if config['add_artwork'] else 'No'}")
        print(f"5. Minimum bitrate: {config['min_bitrate']} kbps")
        print(f"6. Number of workers: {config['max_workers']}")
        print("7. Start download")
        print("8. Paste/Replace saved cookie")
        print("0. Exit")
        print("--------------------------------")

        choice = input("Select an option: ").strip()
        if choice == "1":
            config['playlist_url'] = input("Enter SoundCloud track or playlist URL: ").strip()
        elif choice == "2":
            config['download_folder'] = input("Enter download folder (relative = next to the exe): ").strip()
        elif choice == "3":
            config['authenticate'] = not config['authenticate']
            if config['authenticate'] and not has_saved_cookie():
                print("\nNo saved cookie found.")
                text = prompt_cookie_paste()
                if text:
                    save_cookie_text(text)
                    print(f"Saved cookie to: {COOKIE_PATH}")
                else:
                    print("No cookie pasted; authentication will be disabled.")
                    config['authenticate'] = False
                input("Press Enter to continue...")
        elif choice == "4":
            config['add_artwork'] = not config['add_artwork']
        elif choice == "5":
            try:
                config['min_bitrate'] = int(input("Minimum bitrate (kbps): ").strip())
            except ValueError:
                input("Invalid number. Press Enter to continue...")
        elif choice == "6":
            try:
                config['max_workers'] = max(1, int(input("Number of workers: ").strip()))
            except ValueError:
                input("Invalid number. Press Enter to continue...")
        elif choice == "7":
            if not config['playlist_url']:
                input("Playlist URL is required. Press Enter to continue...")
                continue
            return config
        elif choice == "8":
            text = prompt_cookie_paste()
            if text:
                save_cookie_text(text)
                print(f"Saved cookie to: {COOKIE_PATH}")
                if not config['authenticate']:
                    use_now = input("Enable authentication for this session? [y/N]: ").strip().lower()
                    if use_now.startswith("y"):
                        config['authenticate'] = True
            else:
                print("No cookie pasted.")
            input("Press Enter to continue...")
        elif choice == "0":
            raise SystemExit
        else:
            input("Invalid choice. Press Enter to continue...")

# ------------------------------
# Async: metadata extraction
# ------------------------------
async def fetch_track_urls(playlist_url, authenticate=False, cookiefile=""):
    """Return a list of track dicts for either a playlist URL or a single track URL."""
    loop = asyncio.get_event_loop()

    def extract(cookiefile_arg=None):
        ydl_opts = {"quiet": True, "extract_flat": True}
        if cookiefile_arg:
            ydl_opts["cookiefile"] = cookiefile_arg
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            # Playlist: build list from entries
            entries = info.get("entries")
            if isinstance(entries, list) and entries:
                tracks = []
                for e in entries:
                    if not isinstance(e, dict):
                        continue
                    track_url = e.get("webpage_url") or e.get("url")
                    if not track_url:
                        continue
                    tracks.append({"url": track_url, "thumbnail": e.get("thumbnail")})
                return tracks
            # Single track: return one item
            track_url = info.get("webpage_url") or playlist_url
            return [{"url": track_url, "thumbnail": info.get("thumbnail")}]

    def extract_with_fallback():
        try:
            return extract(None)
        except Exception as e:
            if authenticate and cookiefile and should_retry_with_auth(e):
                return extract(cookiefile)
            raise

    return await loop.run_in_executor(None, extract_with_fallback)

# ------------------------------
# Download, tag, rename, and check bitrate
# ------------------------------
def download_and_tag(track_info, output_folder, ydl_opts_anon, ydl_opts_auth=None, min_bitrate=320, add_artwork=False):
    """Function to download one track and tag it with the metadate that was asked"""
    url = track_info["url"]

    def run_download(opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_path = ydl.prepare_filename(info)
            final_path = os.path.splitext(final_path)[0] + ".mp3"
            return info, final_path

    try:
        # Try anonymous first, then retry with cookies only if needed
        try:
            info, final_path = run_download(ydl_opts_anon)
        except Exception as e_first:
            if ydl_opts_auth and should_retry_with_auth(e_first):
                info, final_path = run_download(ydl_opts_auth)
            else:
                print(f"Error downloading {url}: {e_first}")
                return False

        if not os.path.exists(final_path):
            title = info.get("title") or f"track_{info.get('id','unknown')}"
            artist = info.get("uploader") or "Unknown Artist"
            title_clean = sanitize_filename(title)
            artist_clean = sanitize_filename(artist)
            new_filename = os.path.join(output_folder, f"{artist_clean} - {title_clean}.mp3")
            if os.path.exists(new_filename):
                print(f"Already exists: {artist_clean} - {title_clean}")
                return True
            else:
                print(f"File missing for: {url}")
                return False

        # Check bitrate
        bitrate = get_bitrate(final_path)
        if bitrate < min_bitrate:
            print(f"Skipping {info.get('title')} ({bitrate} kbps < {min_bitrate} kbps)")
            try:
                os.remove(final_path)
            except Exception:
                pass
            return False

        # Tag metadata
        title = info.get("title") or f"track_{info.get('id','unknown')}"
        artist = info.get("uploader") or "Unknown Artist"
        title_clean = sanitize_filename(title)
        artist_clean = sanitize_filename(artist)

        try:
            audio = EasyID3(final_path)
        except Exception:
            audio = EasyID3()
            audio.save(final_path)
            audio = EasyID3(final_path)

        audio["title"] = title
        audio["artist"] = artist
        audio["album"] = "SoundCloud Playlist"
        audio.save(final_path)

        # Add artwork
        if add_artwork:
            thumbnail_url = info.get("thumbnail") or track_info.get("thumbnail")
            if thumbnail_url:
                try:
                    img_data = requests.get(thumbnail_url, timeout=10).content
                    img = Image.open(BytesIO(img_data)).convert("RGB")
                    img_bytes = BytesIO()
                    img.save(img_bytes, format="JPEG")
                    id3 = ID3(final_path)
                    id3.add(APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=img_bytes.getvalue()))
                    id3.save()
                except Exception:
                    pass

        # Rename to Artist - Title.mp3
        new_filename = os.path.join(output_folder, f"{artist_clean} - {title_clean}.mp3")
        if final_path != new_filename:
            counter = 1
            unique_filename = new_filename
            while os.path.exists(unique_filename):
                unique_filename = os.path.join(output_folder, f"{artist_clean} - {title_clean} ({counter}).mp3")
                counter += 1
            shutil.move(final_path, unique_filename)

        return True

    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

# ------------------------------
# Main hybrid downloader
# ------------------------------
async def download_playlist_hybrid(playlist_url, output_folder="downloads", max_workers=6, min_bitrate=320, add_artwork=False, authenticate=False, cookiefile=""):
    # Resolve output folder relative to the executable/script
    output_folder = resolve_path(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    print("Extracting metadata…")
    tracks = await fetch_track_urls(playlist_url, authenticate=authenticate, cookiefile=cookiefile)
    if not tracks:
        print("No tracks found.")
        return

    print(f"Found {len(tracks)} tracks. Downloading with {max_workers} parallel processes…\n")

    ydl_opts_base = {
        "format": "bestaudio[abr>=320]/bestaudio",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }],
        "outtmpl": os.path.join(output_folder, "%(title)s.%(ext)s"),
        "quiet": True,
        "ignoreerrors": True,
        "download_archive": os.path.join(output_folder, "downloaded.txt"),
    }
    ydl_opts_anon = dict(ydl_opts_base)
    ydl_opts_auth = None
    if authenticate and (cookiefile or has_saved_cookie()):
        ydl_opts_auth = dict(ydl_opts_base)
        ydl_opts_auth["cookiefile"] = cookiefile or COOKIE_PATH

    worker = partial(
        download_and_tag,
        output_folder=output_folder,
        ydl_opts_anon=ydl_opts_anon,
        ydl_opts_auth=ydl_opts_auth,
        min_bitrate=min_bitrate,
        add_artwork=add_artwork,
    )
    loop = asyncio.get_event_loop()

    #Launch the downloads of the tracks on multiple threads at a time
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [loop.run_in_executor(executor, worker, track) for track in tracks]
        with tqdm(total=len(futures), desc="Downloading", ncols=80) as pbar:
            for f in asyncio.as_completed(futures):
                _ = await f
                pbar.update(1)

    print("\nAll downloads complete!")

# ------------------------------
# Entry point
# ------------------------------
if __name__ == "__main__":
    multiprocessing.freeze_support()
    try:
        multiprocessing.set_start_method("spawn")
    except RuntimeError:
        pass

    cfg = menu()

    cookiefile = COOKIE_PATH if has_saved_cookie() else ""
    use_auth = bool(cfg["authenticate"] and cookiefile)

    asyncio.run(download_playlist_hybrid(
        playlist_url=cfg["playlist_url"],
        output_folder=cfg["download_folder"],
        max_workers=cfg["max_workers"],
        min_bitrate=cfg["min_bitrate"],
        add_artwork=cfg["add_artwork"],
        authenticate=use_auth,
        cookiefile=cookiefile,
    ))
