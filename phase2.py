from astropy.io import fits # permet de lire les fichiers FITS
import matplotlib.pyplot as plt # sert à afficher et sauvegarder des images.
import cv2 as cv # utilisé ici pour les opérations morphologiques (érosion).
import numpy as np # manipulation efficace de tableaux numériques (images).
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats

# Open and read the FITS file
fits_file = './examples/test_M31_linear.fits'
hdul = fits.open(fits_file) # HDUL : liste d’unités HDU (Header Data Unit)
# chaque HDU contient un header(metadonnees), des données (limage)

# Display information about the file
hdul.info() # le nombre de HDU / leur type / la forme des données (dimensions) / leur taille mémoire

# Access the data from the primary HDU
# hdul[0] → HDU principal
data = hdul[0].data # image stockée sous forme de tableau NumPy

# Access header information
header = hdul[0].header # informations astronomiques (instrument, exposition, etc.)

# Handle both monochrome and color images
if data.ndim == 3: 
    # data.ndim = nombre de dimensions (3 dim = img couleur / 2 dim = img en niveau de gris)
    
    # Color image - need to transpose to (height, width, channels)
    # Cas image couleur = réorganisation des canaux
    if data.shape[0] == 3:  # If channels are first: (3, height, width)
        data = np.transpose(data, (1, 2, 0))
    # If already (height, width, 3), no change needed


    # Normalize the entire image to [0, 1] for matplotlib
    data_normalized = (data - data.min()) / (data.max() - data.min())
    
    # Save the data as a png image (no cmap for color images)
    plt.imsave('./results/original.png', data_normalized)
    
    # Normalize each channel separately to [0, 255] for OpenCV
    image = np.zeros_like(data, dtype='uint8')
    for i in range(data.shape[2]):
        channel = data[:, :, i]
        image[:, :, i] = ((channel - channel.min()) / (channel.max() - channel.min()) * 255).astype('uint8')
else:
    # Monochrome image
    plt.imsave('./results/original.png', data, cmap='gray')
    
    # Convert to uint8 for OpenCV
    image = ((data - data.min()) / (data.max() - data.min()) * 255).astype('uint8')

#Phase 2:
    
image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

cv.imwrite('./results/imageGrey.png', image_gray)

mean, median, std = sigma_clipped_stats(image_gray, sigma=3.0) # retourne moy, mediane et ecarttype
#median = fond de ciel
#std = sigma = le bruit

daofind = DAOStarFinder(
    fwhm=10.0, # Full Width at Half Maximum = Taille moyenne d’une étoile (en pixels)
    threshold=7.0 * std # le seuil de detection
)

sources = daofind(image_gray - median)
print(sources)

mask = np.zeros(image_gray.shape, dtype=np.uint8)

for star in sources:
    x = int(star['xcentroid'])
    y = int(star['ycentroid'])
    mask[y, x] = 255

kernel = np.ones((5, 5), np.uint8)
mask = cv.dilate(mask, kernel)
cv.imwrite('./results/mask.png', mask)

overlay = cv.cvtColor(image_gray, cv.COLOR_GRAY2BGR)
overlay[mask > 0] = [0, 0, 255]
cv.imwrite('./results/overlay.png', overlay)

# Define a kernel for erosion
kernel = np.ones((1, 1), np.uint8) #ligne * colonne
# Perform erosion
eroded_image = cv.erode(image, kernel, iterations=1)

# Save the eroded image 
cv.imwrite('./results/eroded.png', eroded_image)

# Close the file
hdul.close()

"""DAOStarFinder
👉 Le principe est toujours le même :
    Estimer le fond + bruit
    Créer un objet DAOStarFinder
    L’appliquer à l’image
    Récupérer une table d’étoiles détectées
    
    
    
    """