# SoundCloud Downloader

## Description
Cet outil permet de télécharger des playlists SoundCloud en utilisant Python. Il supporte l'authentification pour les pistes protégées et offre diverses options de configuration.

## Structure du projet
```
soundcloud-downloader/
├── check_bitrate.sh                    # Script pour vérifier le bitrate des fichiers
├── ReadMe.md                           # Ce fichier README
├── requirements.txt                    # Liste des dépendances Python
├── soundcloud_playlist_downloader.py   # Script principal Python
├── SoundCloudDownloader.spec           # Fichier de spécification pour PyInstaller
├── build/                              # Dossier de build généré par PyInstaller
└── downloads/                          # Dossier pour les téléchargements
```

## Prérequis
Pour pouvoir utiliser cet outil, il faut avoir Python installé pour télécharger et installer les bibliothèques utilisées dans le projet. Il faudra aussi un gestionnaire de package/environnement comme pip, conda ou anaconda. Pip sera utilisé dans ce guide d'installation.

Lors du développement, Python 3.11 a été utilisé, c'est donc conseillé d'utiliser la même version pour ne pas avoir de problèmes lors du téléchargement des bibliothèques.

Il faut ensuite télécharger les bibliothèques :
```bash
pip install -r requirements.txt
```

## Méthodes d'utilisation

### Générer un fichier exécutable
Pour cette méthode, nous allons utiliser PyInstaller pour générer un fichier exécutable qui pourra être mis n'importe où dans votre ordinateur et exécuté.

#### Création du fichier :
Si vous avez bien téléchargé les bibliothèques, vous devriez pouvoir faire ceci :
```bash
# macOS/Linux
pyinstaller --onefile --name SoundCloudDownloader \
  --icon=icon.icns \
  ./soundcloud_playlist_downloader.py

# Windows
pyinstaller --onefile --name SoundCloudDownloader `
  --icon=icon.ico `
  .\soundcloud_playlist_downloader.py
```

#### Ajouter l'icône (Seulement pour Mac)
Pour ajouter l'icône sur Mac, il faut le faire après avoir généré l'exécutable.

Si vous n'avez pas déjà fileicon :
```bash
brew install fileicon
```

```bash
fileicon set ./dist/SoundCloudDownloader ./icon.icns
```

#### Attention
Si vous avez créé cet exécutable sur un Mac et que vous utilisez un éditeur de code, il faudra déplacer l'exécutable depuis le Finder et non depuis l'éditeur car sinon vous allez simplement déplacer un fichier texte non exécutable.

### Utilisation à travers Python
Vous pouvez aussi lancer le script à travers Python :

Vu que vous avez déjà téléchargé les bibliothèques à travers `pip install -r requirements.txt`, il suffit simplement de lancer le script avec Python.
```bash
python soundcloud_playlist_downloader.py
```
Et voilà !

## Guide d'utilisation

### Options du menu
Voici quelques informations sur comment utiliser cet outil :
- **playlist_url** : L'URL de la playlist SoundCloud que vous souhaitez télécharger.
- **download_folder** : Chemin vers le dossier où vous voulez que les chansons soient téléchargées.
- **authenticate** : Une option permettant d'activer ou désactiver l'authentification. Certains sons sont protégés par l'authentification et l'activation de cette option permet de télécharger ces sons. Quand on active cette option, il va falloir renseigner un cookie, ce cookie vous pouvez le récupérer du site de SoundCloud. Il faut utiliser une extension à votre navigateur comme Cookie-Editor par exemple et exporter vos cookies sous le format Netscape. Vous allez ensuite coller ce cookie quand le programme vous le demande. ***(ATTENTION : il faut taper Entrée sur une ligne vide quand vous collez vos cookies)***. Vos cookies seront sauvegardés dans un fichier pour être réutilisés plus tard si vous réexécutez le programme. Vous pouvez aussi changer le cookie sauvegardé grâce au menu. ***Cette option n'est pas du tout nécessaire pour que le programme fonctionne, si des sons ont besoin d'authentification et que vous ne l'avez pas fournie, ils seront simplement ignorés.***
- **add_artwork** : Une option permettant d'activer et de désactiver le téléchargement des pochettes des chansons.
- **min_bitrate** : Bitrate minimum des sons que l'outil accepte de télécharger (en Kbps).
- **max_workers** : Nombre de cœurs de CPU que l'outil peut utiliser. Plus vous augmentez ce chiffre, plus les téléchargements pourront se faire en parallèle et donc plus toute l'opération ira rapidement.

### Retéléchargement
Quand vous retéléchargez des musiques, ***du moment que le dossier de téléchargement est le même***, elles seront ignorées pour ne pas avoir de doublons. Cela fonctionne seulement si c'est exactement la même musique sur SoundCloud. Si c'est une redistribution, elle risque d'être retéléchargée.