# SAE S3 — Star Reduction — État d’avancement - Problématique / Solutions rencontrées

## Auteur :

- Dhesdin Valentin

## Objectif

Réduire les étoiles sur des images **FITS** (astrophoto) sans dégrader les structures scientifiques (nébuleuse/galaxie) et sans artefacts visibles.

## Outils

Python + venv, `astropy`, `photutils` (DAOStarFinder), `opencv-python` (masques/érosion/flou), `matplotlib` (visu PNG).

---

### Jour 3 - Phase 3 (Détection ML - Dhesdin Valentin)

#### Objectif de la phase 3

Remplacer la détection DAOStarFinder par une séparation **ML** (StarNet) qui fournit directement :

- `starless` : fond du ciel + nébuleuse sans étoiles
- `staronly` : couche étoiles isolée

Puis réduire uniquement la couche étoiles et recombiner les deux.

#### Choix de la méthode ML

- **StarNet (pré-entraîné)** : solution la plus judicieuse ici, car elle fournit directement une séparation **starless / stars** "fiable (si seulement...)" et rapide à intégrer dans le temps imparti.
- **Pré-labelling à partir de DAOStarFinder** : possible, mais le modèle apprendrait à partir de DAO, donc même erreurs -> Aucun intérêt car au mieux on aurait reproduit DAO et au pire : moins bien par rapport à la phase 2
- **Entraîner un ML complet** : Impossible dans ce délai, car il faut construire un dataset traiter les datas, construire les features, labellisé, gérer l’entraînement/validation, faisable mais pas à mon niveau dans le délai imparti.

#### Fait

- Récupération des 2 images générées par StarNet :
  - `starless_*.fit`
  - `starmask_*.fit`
  - Création d’un masque à partir de `staronly`
  - normalisation en [0..1]
  - Adoucissement du masque :
  - **dilatation** + **flou gaussien**
  - Réduction de la couche étoiles
  - Recombinaison

#### Problèmes rencontrés + solutions

- **Comparaison visuelle trompeuse !!!!!(fond plus noir / plus gris)**
- **Solution :** comparer en FITS dans Siril avec le même mode d’affichage et les mêmes zones.
- **Interprétation compliquée des fichiers afin de déterminer quel rendu est le meilleur en png**
- **Solution :** Phase 2 / 3 : générer fichier fit à la fin.
- Ouverture de l'une dans Siril, récuperer le même étirement (MTF) et appliqué sur la deuxième image.
- Sélection de même zones : Endroit (pixel) exact et grossissement exact entre les deux.

#### Différence Phase 2 vs Phase 3 (en 1 phrase)

- **Phase 2 :** on fabrique un masque avec DAOStarFinder puis on choisit automatiquement entre original et érodé via interpolation.
- **Phase 3 :** le ML donne déjà `starless` + `staronly`, on réduit uniquement `staronly`, puis on recombine avec `starless`.

#### Interprétation des résultats

| Méthode                                     | Mesure # | FWHM (px) | Ratio (rondeur) | Rendu                                |
| ------------------------------------------- | -------: | --------: | --------------: | ------------------------------------ |
| **Phase 3 (ML / StarNet)**                  |        1 |      3.39 |            1.00 | Moins étirée, + arrondi              |
| **Phase 3 (ML / StarNet)**                  |        2 |      2.47 |            1.37 | Moins étirée, + arrondi              |
| **Phase 2 (DAOStarFinder + interpolation)** |        1 |      5.10 |            1.42 | Plus large et plus étirée(très peu)  |
| **Phase 2 (DAOStarFinder + interpolation)** |        2 |      2.53 |            1.67 | Taille proche mais plus étirée (peu) |

**Conclusion :** globalement, la phase 3 (ML) donne des étoiles **légèrement moins étirées** et **légèrement plus ronde** que la phase 2 .

<table>
  <tr>
    <th>Phase 2 (DAOStarFinder)</th>
    <th>Phase 3 (StarNet / ML)</th>
  </tr>
  <tr>
    <td width="50%">
    <img src="../results/final_image/image_finale.png"/>
    </td>
    <td width="50%">
   <img src="../results/final_image/final_combined_phase3.png"/>
    </td>
  </tr>
</table>

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
