from astropy.io import fits # permet de lire les fichiers FITS
import matplotlib.pyplot as plt # sert à afficher et sauvegarder des images.
import cv2 as cv # utilisé ici pour les opérations morphologiques (érosion).
import numpy as np # manipulation efficace de tableaux numériques (images).

# Open and read the FITS file
fits_file = './examples/test_M31_linear.fits'
hdul = fits.open(fits_file) # HDUL : liste d’unités HDU (Header Data Unit)
# chaque HDU contient un header(metadonnees), des données (limage)

# Display information about the file
hdul.info() # le nombre de HDU / leur type / la forme des données (dimensions) / leur taille mémoire

# Access the data from the primary HDU
# hdul[0] → HDU principal
data = hdul[0].data # image stockée sous forme de tableau NumPy
print()
print("data :")
print(data)
print()
print("data shape 0 :")
print(data.shape[0])
print()
print("data ndim :")
print(data.ndim)

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
    print("data2 :")
    print(data)
    print() 
    print("data2 shape 0 :")
    print(data.shape[0])
    print() 
    
    print("shape:", data.shape)
    print("hauteur:", data.shape[0])
    print("largeur:", data.shape[1])
    print("canaux:", data.shape[2])
    
    print("canaux:", data[2][0])
    print("canaux:", data[2][1])
    print("canaux:", data[2][2])
    print("canaux:", data[2][100])
    print("canaux:", data[:,:,0])

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



# Define a kernel for erosion
kernel = np.ones((3, 3), np.uint8) #ligne * colonne
# Perform erosion
eroded_image = cv.erode(image, kernel, iterations=2)

eroded_image_color = cv.cvtColor(eroded_image, cv.COLOR_BGR2RGB)
# Save the eroded image 
cv.imwrite('./results/eroded.png', eroded_image)
cv.imwrite('./results/erodedColor.png', eroded_image_color)

# Close the file
hdul.close()