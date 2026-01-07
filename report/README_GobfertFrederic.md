# SAE S3 — Star Reduction — État d’avancement - Problématique / Solutions rencontrées

## Auteur :

- Gobfert Frédéric

## Objectif

Réduire les étoiles sur des images **FITS** (astrophoto) sans dégrader les structures scientifiques (nébuleuse/galaxie) et sans artefacts visibles.

## Outils

Python + venv, `astropy`, `photutils` (DAOStarFinder), `opencv-python` (masques/érosion/flou), `matplotlib` (visu PNG).

---

### Jour 3 - Phase 3 (Fredéric)

#### Objectif de la phase 3

#### Choix de la méthode

#### Fait

#### Problèmes rencontrés + solutions

#### Différence Phase 2 vs Phase 3 (en 1 phrase)

#### Interprétation des résultats

**Conclusion bis:** la phase 3 (ML) rend beaucoup plus noir(sombre) le fond du ciel, ce qui n'est pour moi pas une bonne chose du tout, Starnet touche à ça.

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
