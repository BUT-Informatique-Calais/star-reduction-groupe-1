from astropy.io import fits 
import matplotlib.pyplot as plt
import cv2 as cv 
import numpy as np 
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
import os
from astroquery.astrometry_net import AstrometryNet
import time


DIR_RESULTS_ORIGINAL = './resultsAPI/original/'
DIR_RESULTS_MASK = './resultsAPI/masks/'
DIR_RESULTS_FINAL = './resultsAPI/final_image/'

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

def detect_stars_api(image_gray, header, api_key):
    '''
    upload image to Astrometry.net for detect stars with plate-solving
    get back the object catalog (corr.fits) with real stars positions
    
    :param image_gray: monochrome image
    :param header: FITS header with metadata
    :param api_key: Astrometry.net API key
    :return: sources: table of star positions (xcentroid, ycentroid)
    '''
    # Initialization correct
    ast = AstrometryNet()
    ast.api_key = api_key
    
    temp_fits = "temp_for_api.fits"
    # Keep the header for the API have hints (RA/DEC if there is)
    fits.PrimaryHDU(data=image_gray, header=header).writeto(temp_fits, overwrite=True)

    print("Sending image to Astrometry.net")
    # solve_from_image do everything : upload + wait for job
    # Get the submission_id for ask detailed results
    wcs_header, sub_id = ast.solve_from_image(temp_fits,force_image_upload=True,return_submission_id=True,solve_timeout=300) # 5 min max

    print(f"Image ID : {sub_id}")

    # Wait for jobs be ready
    time.sleep(2)
    sub_info = ast._request('GET', f'https://nova.astrometry.net/api/submissions/{sub_id}')
    jobs = sub_info.json().get('jobs', [])
        
    job_id = jobs[0]

    # Download extracted sources (corr.fits file contains X,Y positions)
    # Use direct URL from astrometry.net results
    source_url = f'https://nova.astrometry.net/corr_file/{job_id}'
    with ast._request('GET', source_url) as r:
        with open('detected_sources.fits', 'wb') as f:
            f.write(r.content)
        
        # Read the sources file
        with fits.open('detected_sources.fits') as hdul:
            sources_data = hdul[1].data
            # Transform to Astropy Table for be compatible and hide stars
            from astropy.table import Table
            sources = Table(sources_data)
            
            # Astrometry.net use field_x and field_y for positions
            sources.rename_column('field_x', 'xcentroid')
            sources.rename_column('field_y', 'ycentroid')
            
            print(f"{len(sources)} stars extracted with the API")
        return sources

        # Clean temporary files
        if os.path.exists(temp_fits): os.remove(temp_fits)
    
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
    return sources

def star_mask(image_gray, sources, radius=6):
    '''
    create a matrix for receive values of stars position from sources
    
    create a matrix with the same size of image and initially full infill with 0
    infill position of star with 1
    
    :param image_gray: image
    :param sources: the array of stars positions from DAOStarFinder
    return: the mask
    '''
    mask = np.zeros(image_gray.shape, dtype=np.float32)

    for star in sources:
        x = int(star['xcentroid'])
        y = int(star['ycentroid'])
        cv.circle(mask, (x, y), radius, 1.0, -1)
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


if __name__ == "__main__":
    
    # --- API CONFIGURATION ---
    # My Astrometry.net API key
    MY_API_KEY = 'racggbxbgnljtvag' 
    
    # Load file
    fits_file = './examples/test_M31_linear.fits'
    data, header = load_fits(fits_file)
    
    # Process image
    image = handler_color_image(data)
    image_gray = convert_in_grey(image)
    save_image(DIR_RESULTS_ORIGINAL + 'imageGrey.png', image_gray, cmap='gray')
    
    # data stars recovery with API
    # Use now the API function who handle 3D -> 2D
    sources = detect_stars_api(image_gray, header, MY_API_KEY)
    
    # mask creation based on real catalog data
    mask = star_mask(image_gray, sources, radius=5)
    save_image(DIR_RESULTS_MASK + 'mask_stars_points.png', mask, cmap='gray')
        
    # Apply Gaussian Blur
    maskFlouGaussien = mask_effects(mask, (3,3), (3,3))
        
    # Erode Image
    Ierode = erode_image(image_gray, (2,2), 3)
    save_image(DIR_RESULTS_FINAL + 'image_erode.png', Ierode, cmap='gray')
        
    # final Image creation
    final_image = combinate_mask_image(maskFlouGaussien, Ierode, image_gray)