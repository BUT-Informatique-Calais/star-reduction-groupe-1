# ============== Imports ===================
from astropy.io import fits
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from photutils.detection import DAOStarFinder
from astropy.stats import mad_std
import os


# ============== Paths + infos principales ===================
# Paths
fits_file = "./examples/test_M31_linear.fits"
os.makedirs("./results", exist_ok=True)

# Open and read the FITS file
hdul = fits.open(fits_file)
# Affiche dans le cmd ce que contient le FITS (nbrs extensions etc)).
hdul.info()
# Récupère l’image principale (matrice de pixels) dans l’extension 0.
data = hdul[0].data
# métadonnées
header = hdul[0].header

# ============== Gestion image couleur(3D) / multi-canal ===================

# Si commence par 3 dimensions, c’est une image “couleur” / multi-canal (3 couches).
if data.ndim == 3:  # si première dim = 3, transpose au format (height, width, channels)
    if data.shape[0] == 3:
        data = np.transpose(data, (1, 2, 0))
    # FITS contient des valeurs bruts (capteur) donc on normalise entre 0 et 1 pour plt
    data_normalized = (data - data.min()) / (data.max() - data.min())
    # Sauvegarde l’image originale en png
    plt.imsave("./results/original.png", data_normalized)

    # Normalise chaque canal séparément en [0, 255] pour OpenCV
    image = np.zeros_like(data, dtype="uint8")  # crée une image vide uint8
    for i in range(data.shape[2]):  # pour chaque canal i (0,1,2) :
        channel = data[:, :, i]  # prends ce canal
        image[:, :, i] = (
            (channel - channel.min())
            / (channel.max() - channel.min())
            * 255  # normalise chaque canal en [0,255]
        ).astype("uint8")
else:
    # Image monochrome
    plt.imsave("./results/original.png", data, cmap="gray")
    # Convert to uint8 for OpenCV
    image = ((data - data.min()) / (data.max() - data.min()) * 255).astype("uint8")

# ============== Gestion Conversion Gris / 2D ===================
# Si image couleur
# gray_image8 = image 2D uint8 (niv de gris) (pour opencv)
# gray_imagefloat = image 2D float32 (pour DAOStarFinder)
# compare rgb et bgr pour choisir la meilleure conversion en gris par rapport à l'écart-type (std)
if image.ndim == 3:
    gray_image8 = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
else:
    gray_image8 = image

gray_imagefloat = gray_image8.astype(np.float32)

# ============== Paramètres DAOStarFinder (Détection Etoile) ===================
# mesure du bruit de fond -> distinguer vraie étoile qu'un pixel (bruitée)
bkg_sigma = mad_std(gray_imagefloat)  # Calcul l'oscillation

# mesure le fond de ciel
median = np.median(gray_imagefloat)  # Médiane des valeurs de pixels

fwhm = 4  # Full Width at Half Maximum -> largeur à mi-hauteur en pixel des étoiles
threshold = (
    5.0 * bkg_sigma
)  # Seuil de détection des étoiles (si threshold dépassé -> étoile)

daostarfinder = DAOStarFinder(fwhm=fwhm, threshold=threshold)
sources = daostarfinder(
    gray_imagefloat - median
)  # Enlève le fond de ciel pour approcher de 0 avant détection
print(
    "======================= Affichage de sources ====================================="
)
print(sources)

# ============== Création d'un masque binaire ===================
mask = np.zeros(
    gray_image8.shape, dtype=np.uint8
)  # crée tableau de même taille que l'image rempli de 0

if sources is not None:
    radius = 3  # rayon autour du pixel à marquer comme étoile
    for star in sources:
        x = int(round(star["xcentroid"]))
        y = int(round(star["ycentroid"]))
        cv.circle(
            mask, (x, y), radius, 255, -1
        )  # mask, x,y, radius,  blanc, -1 remplit le cercle
print(
    "========================== Affichage des paramètres DAOStarFinder : =========================="
)
print("bkg_sigma =", bkg_sigma)
print("threshold =", threshold)
print("nb stars =", 0 if sources is None else len(sources))

# ============== Création d'un overlay ===================
overlay = cv.cvtColor(
    gray_image8, cv.COLOR_GRAY2BGR
)  # converti en BGR pour overlay couleur
overlay[mask > 0] = [0, 0, 255]  # met en rouge
cv.imwrite("./results/overlay_stars.png", overlay)


# ============== Version Erodée de l'image originale ===================
kernel = np.ones((3, 3), np.uint8)
Ierode = cv.erode(gray_image8, kernel, iterations=1)
cv.imwrite("./results/testIeroded_image.png", Ierode)
# ============== Masque (M) Bords adoucis par flou gaussien ===================

M = mask.astype(np.float32) / 255.0
M = cv.GaussianBlur(M, (3, 3), 0)  #
cv.imwrite("./results/testmasque_flou.png", (M * 255).astype(np.uint8))

I = gray_image8.astype(np.float32)
E = Ierode.astype(np.float32)

# ============== Résultat  ===================
Ifinal = (M * E) + ((1 - M) * I)
Ifinal_uint8 = np.clip(Ifinal, 0, 255).astype(np.uint8)
cv.imwrite("./results/result_finaluint8.png", Ifinal_uint8)

# ============== Ecriture image en gris ===================
# Save the eroded image
cv.imwrite("./results/gray_imageuint8.png", gray_image8)
# Close the file
hdul.close()
