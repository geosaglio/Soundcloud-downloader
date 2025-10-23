cd downloads || exit

num_songs=0
num_songs_low_bitrate=0
list_songs_low_bitrate=""
for file in *.mp3; do
    if [ -f "$file" ]; then
        bitrate=$(ffprobe -v error -select_streams a:0 -show_entries stream=bit_rate \
            -of default=noprint_wrappers=1:nokey=1 "$file")
        kbps=$((bitrate / 1000))
        echo "File: $file - Bitrate: ${kbps} kbps"
        num_songs=$((num_songs + 1))
        if [ "$kbps" -lt 320 ]; then
            num_songs_low_bitrate=$((num_songs_low_bitrate + 1))
            list_songs_low_bitrate+="$file ($kbps kbps)\n"
        fi
    else
        echo "No mp3 files found in $playlist"
    fi
done
echo ""
echo "Total songs checked: $num_songs"
echo "Songs with bitrate below 320 kbps: $num_songs_low_bitrate"
if [ "$num_songs_low_bitrate" -gt 0 ]; then
    echo -e "List of songs with bitrate below 320 kbps:\n$list_songs_low_bitrate"
fi