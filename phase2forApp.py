from astropy.io import fits 
import matplotlib.pyplot as plt
import cv2 as cv 
import numpy as np 
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
import os


DIR_RESULTS_ORIGINAL = './results/original/'
DIR_RESULTS_MASK = './results/masks/'
DIR_RESULTS_FINAL = './results/final_image/'

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
    print()
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

def handler_color_image(data):
    '''
    Handle both monochrome and color images
    
    if data have 3 channels, it's a color image and maybe need a transposition
    else the image is monochrome and don't need that
    In all case, the image is normalized and saved as original in defaults' directory
    
    :param data: Image
    return: normalized image
    '''
    if data.ndim == 3:
        # Color image - need to transpose to (height, width, channels)
        if data.shape[0] == 3:  # If channels are first: (3, height, width)
            data = np.transpose(data, (1, 2, 0))
        # If already (height, width, 3), no change needed
        
        image = normalize_img(data)
        # Save the data as a png image (no cmap for color images)
        save_image(DIR_RESULTS_ORIGINAL + 'original.png', image)
        
    else:
        # Monochrome image - no need to transpose anything
        image = normalize_img(data)
        save_image(DIR_RESULTS_ORIGINAL + '/original.png', data, cmap='gray')
    return image

def save_image(path, data, cmap=None):
    '''
    Save an image in a directory with an option color
    
    :param path: the path to save
    :param data: the file to save
    :param cmap: the otpion color. for example : cmap='grey'
    '''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.imsave(path, data, cmap=cmap)

def convert_in_grey(image):
    '''
    if the image is a color image, convert this in grey
    
    compare the number of channels to determinate the color of image and 
    realize a mean of the 3 channels for convert in grey
    it's a necessary condition for use DAOStarFinder
    
    :param image: image
    return: the image converted in a float32 format
    '''
    if image.ndim == 3:
        # Mean of 3 channels
        image_gray = np.mean(image, axis=2).astype(np.float32)
    else:
        image_gray = image.astype(np.float32)
    return image_gray

def detect_stars(image_gray, fwhm, threshold, sigma=3.0):
    '''
    use DAOStarFinder of library photutils for detect star in the image
    
    calculate with an astronomy's function mean, median and standard deviation
    Then search star and repertory them in an array with mainly columns above:
    xcentroid, ycentroid (source's position)
    
    :param image_gray: the image eventually converted in grey (required for DAOStarFinder)
    :param fwhm: Full Width at Half Maximum = size of star in pixel
    :param threshold: the detection threshold
    :param sigma: std for delete outliers values
    :return: an array of stars positions
    '''
    # calculate mean, median (= background level), std (=background noise)
    mean, median, std = sigma_clipped_stats(image_gray, sigma=sigma)

    daofind = DAOStarFinder(
        fwhm = fwhm,
        threshold = threshold * std
    )

    sources = daofind(image_gray - median)
    
    print(
    "\n========================== Affichage des paramètres DAOStarFinder : =========================="
    )
    print("sigma = ", sigma)
    print("fhwm = ", fwhm)
    print("threshold = ", threshold)
    print("nb stars = ", 0 if sources is None else len(sources))
    
    return sources

def star_mask(image_gray, sources):
    '''
    create a matrix for receive values of stars position from sources
    
    create a matrix with the same size of image and initially full infill with 0
    infill position of star with 1
    create an overlay to visualize stars will have a traitment
    
    :param image_gray: image
    :param sources: the array of stars positions from DAOStarFinder
    return: the mask
    '''
    print(
    "\n======================= Affichage des colonnes de sources ====================================="
    )
    print(sources.colnames if sources is not None else print("No sources found")) 
    
    mask = np.zeros(image_gray.shape, dtype=np.float32)
    
    for star in sources:
        x = int(star['xcentroid'])
        y = int(star['ycentroid'])
        mask[y, x] = 1.0
    
    # overlay for visualize stars wich will have a traitment
    kernel_for_overlay = np.ones((3,3), np.float32)
    mask_dilate_for_overlay = cv.dilate(mask, kernel_for_overlay)
    # normalize with uint8 for use cvtColor
    image_gray_uint8 = ((image_gray - image_gray.min()) / (image_gray.max() - image_gray.min()) * 255.0 ).astype(np.uint8)
    overlay = cv.cvtColor(image_gray_uint8, cv.COLOR_GRAY2BGR)
    overlay[mask_dilate_for_overlay > 0] = [0, 0, 255]  # red color
    os.makedirs(os.path.dirname(DIR_RESULTS_MASK + "overlay_stars.png"), exist_ok=True)
    cv.imwrite(DIR_RESULTS_MASK + "overlay_stars.png", overlay)
    
    return mask

def mask_effects(mask, kernelDilate=(3,3), kernelGaussian=(3,3)):
    '''
    Apply a dilation on stars of the mask and apply a gaussian blur
    
    save an image of results : the masks with stars dilated and the mask with gaussian blur applied
    
    :param mask: the star mask
    :param kernelDilate: couple of integers who determinate the size of kernel for the dilation of stars before gaussian blur
    :param kernelGaussian: couple of integers who determinate the size of kernel for the gaussian blur
    '''
    # thickening of the star mask
    kernel = np.ones(kernelDilate, np.float32)
    mask_dilate = cv.dilate(mask, kernel)
    save_image(DIR_RESULTS_MASK + 'mask_stars_dilate.png', mask_dilate, cmap='gray')

    # Gaussian blur of the mask
    maskFlouGaussien = cv.GaussianBlur(
        mask_dilate,
        ksize = kernelGaussian,
        sigmaX = 0
    )
    maskFlouGaussien = np.clip(maskFlouGaussien, 0.0, 1.0)
    save_image(DIR_RESULTS_MASK + 'maskFlouGaussien.png', maskFlouGaussien, cmap='gray')
    
    return maskFlouGaussien

def erode_image(image_gray, kernelErode=(2,2), nbIteration=1):
    '''
    return an image eroded with a kernel with size (2,2) parameter and a number of iterations
    
    :param image_gray: image
    :param kernelErode: couple of integer who determinate the size of stars to erode
    :param nbIteration: integer number of eroded waves
    '''
    kernel_erode = np.ones(kernelErode, np.float32)
    Ierode = cv.erode(image_gray, kernel_erode, iterations=nbIteration)
    return Ierode

def combinate_mask_image(mask, imgEroded, image_origin):
    '''
    Combinate the mask with the erodedImage and the origin image
    
    :param mask: the mask
    :param imgEroded: the eroded image
    :param image_origin: the origin image convert in grey
    '''
    final_image = (mask * imgEroded) + ((1 - mask) * image_origin)
    save_image(DIR_RESULTS_FINAL + 'image_finale.png', final_image, cmap='gray')
    return final_image

def display_datatype_check(image_gray, Ierode, final_image):
    '''
    Function to check datatype of the differents images to ensure they keep float32 format during the processus
    
    :param image_gray: the grey image
    :param Ierode: the eroded image
    :param final_image: the final image
    '''
    print("\n======================= check du datatype =============================")
    print("datatype grayimage:", image_gray.dtype)
    print("datatype Ierode:", Ierode.dtype)
    print("datatype Ifinal:", final_image.dtype)


if __name__ == "__main__":
    
    # Load file
    fits_file = './examples/test_M31_linear.fits'
    data, header = load_fits(fits_file)
    
    # Process image
    image = handler_color_image(data)
    image_gray = convert_in_grey(image)
    save_image(DIR_RESULTS_ORIGINAL + 'imageGrey.png', image_gray, cmap='gray')
    
    # data stars recovery and creation of mask
    sources = detect_stars(image_gray, fwhm=4.0, threshold=5.0)
    mask = star_mask(image_gray, sources)
    save_image(DIR_RESULTS_MASK + 'mask_stars_points.png', mask, cmap='gray')
    
    # Apply Gaussian Blur
    maskFlouGaussien = mask_effects(mask, (3,3), (3,3))
    
    # Erode Image
    Ierode = erode_image(image_gray, (2,2), 3)
    save_image(DIR_RESULTS_FINAL + 'image_erode.png', Ierode, cmap='gray')
    
    # creation final Image
    final_image = combinate_mask_image(maskFlouGaussien, Ierode, image_gray)

    display_datatype_check(image_gray, Ierode, final_image)
    

    