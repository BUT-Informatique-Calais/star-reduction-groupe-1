from astropy.io import fits
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np

# Open and read the FITS file
fits_file = "./examples/test_M31_linear.fits"
hdul = fits.open(fits_file)

# Affiche dans le cmd ce que contient le FITS (nbrs extensions etc)).
hdul.info()

# Récupère l’image principale (matrice de pixels) dans l’extension 0.
data = hdul[0].data

# Récupère les métadonnées dans l’extension 0.
header = hdul[0].header

# Si data a 3 dimensions, c’est une image “couleur” / multi-canal (3 couches).
if (
    data.ndim == 3
):  # Trois canaux (axes) pour une image couleur (RGB) ici c'est (3, height, width)
    # Image couleur - besoin de transposer en (height, width, channels)
    if (
        data.shape[0] == 3
    ):  # Si la première dimension est 3, on transpose pour avoir (height, width, 3 demandé par plt et cv)
        data = np.transpose(
            data,
            (1, 2, 0),  # 0 devient 2(canaux), 1 devient 0(height), 2 devient 1(width)
        )  # data devient (height, width, 3(canaux)) 1,2,0 pour permuter les axes

    # SI la dernière dimension est 3, c'est déjà bon.

    # FITS contient des valeurs bruts (capteur) donc on normalise entre 0 et 1 pour plt
    # car plt.imsave attend des valeurs entre 0 et 1 pour les images en float
    data_normalized = (data - data.min()) / (data.max() - data.min())

    # Save the data as a png image (no cmap for color images)
    plt.imsave("./results/original.png", data_normalized)

    # Normalize each channel separately to [0, 255] for OpenCV
    image = np.zeros_like(data, dtype="uint8")  # crée une image vide uint8
    for i in range(data.shape[2]):  # pour chaque canal i (0,1,2) :
        channel = data[:, :, i]  # prends ce canal
        image[:, :, i] = (
            (channel - channel.min())
            / (channel.max() - channel.min())
            * 255  # normalise chaque canal en [0,255]
        ).astype("uint8")
else:
    # Monochrome image
    plt.imsave("./results/original.png", data, cmap="gray")

    # Convert to uint8 for OpenCV
    image = ((data - data.min()) / (data.max() - data.min()) * 255).astype("uint8")


# Define a kernel for erosion
kernel = np.ones((4, 4), np.uint8)
# Perform erosion
eroded_image = cv.erode(image, kernel, iterations=1)


eroded_color = cv.cvtColor(eroded_image, cv.COLOR_BGR2RGB)
cv.imwrite("./results/eroded_rgb.png", eroded_color)

# Save the eroded image
cv.imwrite("./results/eroded_bgr.png", eroded_image)

# Close the file
hdul.close()
