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

- Dossier results/original
  - Original (Image original fourni)
- Dossier results/mask
  - Masque (Masque binaire sur étoile détectée)
  - Masque Flou Gaussien (Reprise du masque binaire avec)
  - Overlay
- Dossier results/image_final
  - Ierode
  - Image grise original
  - IMage final
