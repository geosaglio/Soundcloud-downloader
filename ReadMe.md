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

#### Attention
Si vous avez creer cette executable sur un mac et que vous utilisez un editeur de code, il faudras déplacer l'éxécutable depuis le Finder et non depuis l'éditeur car sinon vous allez simplement déplacer un ficher text non éxécutable.

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
- authenticate: Une option permettant d'acctiver ou désactiver l'authentification. Certatains sons sont protéger par l'authentification et l'activation de cette option permet de télécharger ces sons. Quand on active cette option, il vas faloir renseigner un cookie, ce cookie vous pouvez le récupérer du site de soundcloud. Il faut utiliser une extension a votre navigateur comme cookie-editor par exemple et éxporter vos cookies sous le format Netscape. Vous allet ensuite coller ce cookie quand le programme vous le demande. ***(ATTETION: il faut taper entrer sur une ligne vide quand vous coller vos cookies)***. Vos cookies seront sauvegarder dans un fichier pour être réutiliser plus tard si vous reéxécuter le programme. Vous pouvez aussi changer le cookie sauvegarder grace au menu. ***Cette option n'est pas du tout nécéssaire pour que le programme fonctionne, si des sons ont besoin d'authentification et que vous ne l'avez pas fourni ils seront simplement skip.***
- add_artwork: Une option permettant de activer et de désactiver le téléchargement des pochettes des chansons
- min_bitrate: Bitrate minimum des sons que l'outil accepte de télécharger (en Kbps)
- max_workers: Nombre de coeur de CPU que l'outil peut utiliser. Le plus vous augmenter ce chiffre le plus les téléchargement pourront se faire en parallel et donc le plus toute l'oppération vas aller rapidement.
### Retéléchargement
Quand vous retélécharger des musiques, ***du temps que le dossier de téléchargement est le même*** elles seront skip pour pas avoir de doublons. Ceci fonctionne que si c'est exactement la même musique sur soundcloud. Si c'est une redistribution, elle risque d'être retélécharger