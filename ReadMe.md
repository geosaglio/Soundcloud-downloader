# Soundcloud downloader
## Prérequis
Pour pouvoir utiliser cette outil if faut avoir python pour télécharger et installer les bibliothèques utiliser dans le projet. Il faudras aussi un gestionaire de package/environement comme pip, conda ou anaconda. pip sera utiliser dans ce guide d'installation.

Lors du développement, Python 3.11 a été utiliser, c'est donc conseiller d'utiliser la même version pour ne pas avoir de problem lors du téléchargement des bibliothèques

Il faut ensuite télécharger les bibliothèques
``` bash
pip install -r requirements.txt
```
## Méthodes d'utilisation
### Générer un fichier éxecutable
Pour cette méthode, nous allons utiliser pyinstaller pour générer un fichier éxecutable qui pourras être mis n'import ou dans votre ordinateur et éxecuter.
#### Creation du fichier:
Si vous avez bien télécharger les bibliothèques, vous devriez pouvoire faire ceci:
``` bash
# MacOs/Linux
pyinstaller --onefile --name SoundCloudDownloader \
  --icon=icon.icns \
  ./soundcloud_playlist_downloader.py

# Windows
pyinstaller --onefile --name SoundCloudDownloader `
  --icon=icon.ico `
  .\soundcloud_playlist_downloader.py
```

#### Ajouter l'icon (Seulement pour mac)
Pour ajouter l'icon sur mac il faut le faire après avoir générer l'éxecutable.

SI vous avez pas déjà fileicon:
``` bash
brew install fileicon
```

``` bash
fileicon set ./dist/SoundCloudDownloader ./icon.icns
```

### Utilisation a travers Python
Vous pouvez aussi lancer le script a travers python:

Vue que vous avez déjà télécharger les bilbiothèques a travers ```pip install -r requirements.txt```, il suffit simplement de lancer le script avec python.
``` bash
python soundcloud_playlist_downloader.py
```
Et voila!

## Guide d'utilisation
### Menu options
Voici quelques information de comment utiliser cette outil:
- playlist_url: L'URL de la playlist soundcloud que vous souhaitez télécharger.
- download_folder: Chemin vers le fichier ou vous voulez que les chansons soit télécharger
- authenticate: Une option permettant d'acctiver ou désactiver l'authentification. Certatains sons sont protéger par l'authentification et l'activation de cette option permet de télécharger ces sons
  - cookiefile: Pour l'utiliser, il faut aller sur le site de soundcloud, utiliser une extesion dans votre navigateur comme Cookie-editor ou autre pour exporter vous cookie sous le format Netscape. Une fois que vous avez vous cookie, copier les dans un fichier et indiquer le chemin vers se fichier dans cette option du menu. 
- add_artwork: Une option permettant de activer et de désactiver le téléchargement des pochettes des chansons
- min_bitrate: Bitrate minimum des sons que l'outil accepte de télécharger (en Kbps)
- max_workers: Nombre de coeur de CPU que l'outil peut utiliser. Le plus vous augmenter ce chiffre le plus les téléchargement pourront se faire en parallel et donc le plus toute l'oppération vas aller rapidement.
### Retéléchargement
Quand vous retélécharger des musiques, *** du temps que le dossier de téléchargement est le même*** elles seront skip pour pas avoir de doublons. Ceci fonctionne que si c'est exactement la même musique sur soundcloud. Si c'est une redistribution, elle risque d'être retélécharger