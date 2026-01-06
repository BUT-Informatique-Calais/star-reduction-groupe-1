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
os.makedirs("./results/fits", exist_ok=True)

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
data = data.astype(np.float32)
if data.ndim == 3:  # si première dim = 3, transpose au format (height, width, channels)
    if data.shape[0] == 3:
        data = np.transpose(data, (1, 2, 0))
    # FITS contient des valeurs bruts (capteur) donc on normalise entre 0 et 1 pour plt
    data_normalized = (data - data.min()) / (data.max() - data.min())
    # Sauvegarde l’image originale en png
    plt.imsave("./results/original.png", data_normalized)

    # On garde l'échelle fits
    image = data
else:
    # Image monochrome
    data_normalized = (data - data.min()) / (data.max() - data.min())
    plt.imsave("./results/original.png", data_normalized, cmap="gray")
    # Convert to float32 for processing
    image = data

# ============== Gestion Conversion Gris / 2D ===================
# Si image couleur
# gray_image8 = image 2D uint8 (niv de gris) (pour opencv)
# gray_imagefloat = image 2D float32 (pour DAOStarFinder)
# compare rgb et bgr pour choisir la meilleure conversion en gris par rapport à l'écart-type (std)
if image.ndim == 3:
    gray_image8 = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
else:
    gray_image8 = image

gray_imagefloat = gray_image8.astype(np.float32)  # image fits float pour calcul
gray_image8 = (
    (gray_imagefloat - gray_imagefloat.min())
    / (gray_imagefloat.max() - gray_imagefloat.min())
    * 255.0
).astype(np.uint8)
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

fits.writeto(
    "./results/fits/gray_float.fits", gray_imagefloat, header=header, overwrite=True
)
# ============== Version Erodée de l'image originale ===================
kernel = np.ones((3, 3), np.uint8)
Ierode = cv.erode(gray_imagefloat, kernel, iterations=1)
fits.writeto("./results/fits/Ieroded.fits", Ierode, header=header, overwrite=True)
# ============== Masque (M) Bords adoucis par flou gaussien ===================


M = mask.astype(np.float32) / 255.0
M = cv.GaussianBlur(M, (3, 3), 0)  #
cv.imwrite("./results/testmasque_flou.png", (M * 255).astype(np.uint8))

I = gray_imagefloat
E = Ierode
Ifinal = (M * E) + ((1 - M) * I)


print("============= check du datatype ===================")
print("datatype grayimage:", gray_imagefloat.dtype)
print("datatype Ierode:", Ierode.dtype)
print("datatype Ifinal:", Ifinal.dtype)

# ============== Résultat  ===================

fits.writeto(
    "./results/fits/result_final.fits",
    Ifinal,
    header=header,
    overwrite=True,
)


# ============== Affichage PLT gray image ===================
plt_result_gray = fits.getdata("./results/fits/gray_float.fits")

# stretch simple < 1% et > 99% ignore pour voir quelque chose
vmin, vmax = np.percentile(plt_result_gray, (1, 99))

plt.figure(figsize=(8, 8))
plt.imshow(plt_result_gray, cmap="gray", vmin=vmin, vmax=vmax)
plt.axis("off")
plt.savefig("./results/plt_gray_float.png", bbox_inches="tight", pad_inches=0)
# ============== Affichage Resultat Erode ===================
plt_result_eroded = fits.getdata("./results/fits/Ieroded.fits")

# stretch simple < 1% et > 99% ignore pour voir quelque chose
vmin, vmax = np.percentile(plt_result_eroded, (1, 99))

plt.figure(figsize=(8, 8))
plt.imshow(plt_result_eroded, cmap="gray", vmin=vmin, vmax=vmax)
plt.axis("off")
plt.savefig("./results/plt_result_eroded.png", bbox_inches="tight", pad_inches=0)


# ============== Affichage résultat final ===================
plt_result_final = fits.getdata("./results/fits/result_final.fits")

# stretch simple < 1% et > 99% ignore pour voir quelque chose
vmin, vmax = np.percentile(plt_result_final, (1, 99))

plt.figure(figsize=(8, 8))
plt.imshow(plt_result_final, cmap="gray", vmin=vmin, vmax=vmax)
plt.axis("off")
plt.savefig("./results/plt_result_final.png", bbox_inches="tight", pad_inches=0)

# ============== Ecriture image en gris ===================
# Save the eroded image
cv.imwrite("./results/gray_image.png", gray_image8)
# Close the file
hdul.close()
