from astropy.io import fits # permet de lire les fichiers FITS
import matplotlib.pyplot as plt # sert à afficher et sauvegarder des images.
import cv2 as cv # utilisé ici pour les opérations morphologiques (érosion).
import numpy as np # manipulation efficace de tableaux numériques (images).
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats


def load_fits(path: str):
    '''
    open and read the FITS file
    take information and close file
    
    :param path: the image's path
    :type path: str
    :return: data: the image and header: file's informations
    '''
    hdul = fits.open(path) # Header Data Unit
    # Display information about the file
    hdul.info()
    
    # Access the data from the primary HDU
    data = hdul[0].data
    # Access header information
    header = hdul[0].header

    # Close the file
    hdul.close()
    
    return data, header


def normalize_img(data):
    '''
    Normalize the entire image to [0, 1] for matplotlib
    
    :param data: the image previously loaded
    '''
    image = (data - data.min()) / (data.max() - data.min())
    image = image.astype(np.float32)
    return image


if __name__ == "__main__":
    fits_file = './examples/test_M31_linear.fits'
    data, header = load_fits(fits_file)
    
    
    

    # Handle both monochrome and color images

    if data.ndim == 3: 
        # data.ndim = nombre de dimensions (3 dim = img couleur / 2 dim = img en niveau de gris)
        
        # Color image - need to transpose to (height, width, channels)
        # Cas image couleur = réorganisation des canaux
        if data.shape[0] == 3:  # If channels are first: (3, height, width)
            data = np.transpose(data, (1, 2, 0))
        # If already (height, width, 3), no change needed

        # Normalize the entire image to [0, 1] for matplotlib
        image = normalize_img(data)
        
        # Save the data as a png image (no cmap for color images)
        plt.imsave('./results/original.png', image)
        
    else:
        
        # Normalize the entire image to [0, 1] for matplotlib
        image = normalize_img(data)
        
        # Monochrome image = garder en float 32
        plt.imsave('./results/original.png', data, cmap='gray')


    #Phase 2:
    # Conversion couleur → monochrome float32
    if image.ndim == 3:
        # Moyenne simple des 3 canaux
        image_gray = np.mean(image, axis=2).astype(np.float32)
    else:
        image_gray = image.astype(np.float32)

    plt.imsave('./results/imageGrey.png', image_gray, cmap='gray')

    # detection des etoiles
    mean, median, std = sigma_clipped_stats(image_gray, sigma=3.0) # retourne moy, mediane et ecarttype
    #median = fond de ciel
    #std = sigma = le bruit

    daofind = DAOStarFinder(
        fwhm=4.0, # Full Width at Half Maximum = Taille moyenne d’une étoile (en pixels)
        threshold=5.0 * std # le seuil de detection
    )

    sources = daofind(image_gray - median)

    #creation  masque flou gaussien

    mask = np.zeros(image_gray.shape, dtype=np.float32)

    for star in sources:
        x = int(star['xcentroid'])
        y = int(star['ycentroid'])
        mask[y, x] = 1.0

    # a ce stade points blancs = etoiles
    plt.imsave('./results/mask_stars_points.png', mask, cmap='gray')

    # epaississement du masque
    kernel = np.ones((3, 3), np.float32)
    mask_dilate = cv.dilate(mask, kernel)
    plt.imsave('./results/mask_stars_dilate.png', mask_dilate, cmap='gray')

    # Flou gaussien du masque
    maskFlouGaussien = cv.GaussianBlur(
        mask_dilate,
        ksize = (3,3), # taille du filtre / le noyau / doit etre impair (pour avoir un centre)
        sigmaX = 0 # petit = peu de flou = details conserves
    )
    maskFlouGaussien = np.clip(maskFlouGaussien, 0.0, 1.0)
    plt.imsave('./results/maskFlouGaussien.png', maskFlouGaussien, cmap='gray')

    kernel_erode = np.ones((2,2), np.float32)
    Ierode = cv.erode(image_gray, kernel_erode, iterations=3)

    plt.imsave('./results/image_erode.png', Ierode, cmap='gray')


    # calcul de limage finale
    # maskM = le masque
    image_finale = (maskFlouGaussien * Ierode) + ((1 - maskFlouGaussien) * image_gray)
    plt.imsave('./results/image_finale.png', image_finale, cmap='gray')

    image_finale_int8 = (np.clip(image_finale, 0.0, 1.0) * 255).astype(np.uint8)
    cv.imwrite('./results/image_finale_CV.png', image_finale_int8)




    