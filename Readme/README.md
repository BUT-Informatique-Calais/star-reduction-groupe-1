# SAE S3 — Star Reduction — État d’avancement - Problématique / Solutions rencontrées

## Objectif

Réduire les étoiles sur des images **FITS** (astrophoto) sans dégrader les structures scientifiques (nébuleuse/galaxie) et sans artefacts visibles.

## Outils

Python + venv, `astropy`, `photutils` (DAOStarFinder), `opencv-python` (masques/érosion/flou), `matplotlib` (visu PNG).

---

## Jour 1 — Phase 1 terminée + début Phase 2

### Fait

- Prise en main du format **FITS** (données float + header).
- Lecture FITS et export PNG de visualisation.
- **Phase 1** : érosion globale OpenCV (kernel, itérations) + observation des résultats.
- Début **Phase 2** : mise en place de la détection d’étoiles (DAOStarFinder) et du masque binaire avec apprentissage des paramètres.

### Difficultés + solutions

- **Conflits pip / versions (numpy vs opencv)** → ajustement des versions dans `requirements.txt` (versions compatibles numpy <2.3).
- **Érosion globale = perte de détails :** méthode non sélective, elle dégrade aussi la galaxie/nébuleuse.

---

## Jour 2 — Phase 2 terminée (A + B)

### Étape A : masque d’étoiles

- Détection via `DAOStarFinder` avec :
  - bruit de fond estimé par `mad_std`
  - fond de ciel par `median`
  - paramètres ajustés (`fwhm`, `threshold`)
- Création d’un masque binaire : fond noir (0), étoiles en blanc (255) via cercles sur les centroids.
- Vérification via un overlay (étoiles en rouge).

### Étape B : réduction localisée

- Calcul sur **image grise FITS float** (pas en 0..255 pour les traitements car trop de perte de qualité).
- Création `Ierode` (érosion) sur l’image float.
- Flou gaussien du masque (bords doux)
- Mélange progressif : Ifinal = (M × Ierode) + ((1 − M) × Ioriginal)
- Exports :
  - PNG de visualisation via `matplotlib` avec imsave et pas en créeant de figure car pour du traitement d'image, il vaut mieux garder le PNG pixel pour pixel.

### Difficultés + solutions

-
- **Compréhension/tuning `fwhm` et `threshold`** → tests : baisse de `fwhm` + ajustement `threshold` pour mieux détecter les étoiles utiles.
- **Différence entre uint8 et float en rendu final** : la différence est surtout importante pour préserver la précision scientifique : Travailler au maximum en float32

---

## Execution et interprétation des résultats :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Examples files

Example files are located in the `examples/` directory. You can run the scripts with these files to see how they work.

- Example 1 : `examples/HorseHead.fits` (Black and whiteFITS image file for testing)
- Example 2 : `examples/test_M31_linear.fits` (Color FITS image file for testing)
- Example 3 : `examples/test_M31_raw.fits` (Color FITS image file for testing)

## Preview : 
- Dossier results/
    - 



## Jour 3 — Phase 3 : Astrométrie via API (Terminée)

## Fait 
Documentation et recherche : Étude du fonctionnement de l'API Astrometry.net et de la librairie astroquery pour l'envoi et la récupération de données distantes.

Intégration API : Envoi de l'image pour un "Plate-solving" (reconnaissance du champ d'étoiles via base de données mondiale).

Récupération du catalogue : Extraction du fichier corr.fits contenant les positions exactes ($X, Y$) des étoiles confirmées par l'API.

## Difficultés + solutions 

Fichier temporaire indispensable : L'API nécessite un fichier physique avec son Header pour fonctionner. Solution : Création d'un temp_for_api.fits incluant les données et l'entête d'origine, supprimé automatiquement après l'envoi.

Bug de réception astroquery : L'envoi fonctionnait mais la récupération des résultats (jobs / données) échouait malgré un envoi réussi.  Solution : Contournement via des requêtes HTTP directes (ast._request) sur l'URL du Job ID pour forcer le téléchargement du catalogue.

Erreur "No SIMPLE card" : Problème de lecture du fichier retourné par le serveur. Solution : Lecture forcée via Table(hdul[1].data) pour extraire proprement les colonnes field_x et field_y.

Suite à un échec de push causé par des conflits de versions sur astroquery et des fichiers de configuration corrompus, j'ai dû supprimer et reconstruire l'environnement virtuel (.venv). Cette purge a permis de réinstaller proprement les dépendances via pip et de débloquer la synchronisation avec la branche API.
