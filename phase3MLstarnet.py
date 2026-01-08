from astropy.io import fits
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
from photutils.detection import DAOStarFinder
from astropy.stats import sigma_clipped_stats
import os


DIR_RESULTS_ORIGINAL = "./results/original/"
DIR_RESULTS_MASK = "./results/masks/"
DIR_RESULTS_FINAL = "./results/final_image/"


def load_fits(path: str):
    """
    open and read the FITS file
    take information and close file

    :param path: the image's path
    :type path: str
    :return: data: the image and header: file's informations
    """
    hdul = fits.open(path)  # Header Data Unit
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
    """
    Normalize the entire image to [0, 1] for matplotlib

    :param data: the image previously loaded
    """
    image = (data - data.min()) / (data.max() - data.min())
    image = image.astype(np.float32)
    return image


def handler_color_image(data):
    """
    Handle both monochrome and color images

    if data have 3 channels, it's a color image and maybe need a transposition
    else the image is monochrome and don't need that
    In all case, the image is normalized and saved as original in defaults' directory

    :param data: Image
    return: normalized image
    """
    if data.ndim == 3:
        # Color image - need to transpose to (height, width, channels)
        if data.shape[0] == 3:  # If channels are first: (3, height, width)
            data = np.transpose(data, (1, 2, 0))
        # If already (height, width, 3), no change needed

        image = normalize_img(data)
        # Save the data as a png image (no cmap for color images)
        save_image(DIR_RESULTS_ORIGINAL + "original.png", image)

    else:
        # Monochrome image - no need to transpose anything
        image = normalize_img(data)
        save_image(DIR_RESULTS_ORIGINAL + "/original.png", image, cmap="gray")
    return image


def save_image(path, data, cmap=None):
    """
    Save an image in a directory with an option color

    :param path: the path to save
    :param data: the file to save
    :param cmap: the otpion color. for example : cmap='grey'
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.imsave(path, data, cmap=cmap)


def convert_in_grey(image):
    """
    if the image is a color image, convert this in grey

    compare the number of channels to determinate the color of image and
    realize a mean of the 3 channels for convert in grey
    it's a necessary condition for use DAOStarFinder

    :param image: image
    return: the image converted in a float32 format
    """
    if image.ndim == 3:
        # Mean of 3 channels
        image_gray = np.mean(image, axis=2).astype(np.float32)
    else:
        image_gray = image.astype(np.float32)
    return image_gray


def mask_from_stars_starnet(stars_img, thresh=0.02):
    """
    stars_img : image stars-only (déjà normalisée 0..1 idéalement)
    thresh : seuil pour dire "ici il y a une étoile"
    """
    if stars_img.ndim == 3:
        stars_gray = np.mean(stars_img, axis=2).astype(np.float32)
    else:
        stars_gray = stars_img.astype(np.float32)

    normalize = normalize_img(stars_gray)
    mask = (normalize > thresh).astype(np.float32)

    save_image(DIR_RESULTS_MASK + "mask_stars_thresh.png", mask, cmap="gray")

    return mask


def mask_effects(mask, kernelDilate=(3, 3), kernelGaussian=(3, 3), iterations=1):
    """
    pply a dilation on stars of the mask and apply a gaussian blur

    save an image of results : the masks with stars dilated and the mask with gaussian blur applied

    :param mask: the star mask
    :param kernelDilate: couple of integers who determinate the size of kernel for the dilation of stars before gaussian blur
    :param kernelGaussian: couple of integers who determinate the size of kernel for the gaussian blur
    :param iterations: number of iterations for dilation
    """
    # thickening of the star mask
    kernel = np.ones(kernelDilate, np.float32)
    mask_dilate = cv.dilate(mask, kernel, iterations=iterations)
    save_image(DIR_RESULTS_MASK + "mask_stars_dilate.png", mask_dilate, cmap="gray")

    # Gaussian blur of the mask
    maskFlouGaussien = cv.GaussianBlur(mask_dilate, ksize=kernelGaussian, sigmaX=0)
    maskFlouGaussien = np.clip(maskFlouGaussien, 0.0, 1.0)
    save_image(DIR_RESULTS_MASK + "star_blurred.png", maskFlouGaussien, cmap="gray")

    return maskFlouGaussien


def reduce_stars(stars_img, mask, alpha=0.5):
    """
    Reduce stars in the star image using the mask

    :param stars_img: the star-only image
    :param mask: the mask
    :param alpha: reduction factor (0 = no reduction, 1 = full removal)
    """

    # alpha in 0 and 1
    alpha = float(np.clip(alpha, 0.0, 1.0))
    # apply reduction
    star_reduced = stars_img * (1 - alpha * mask)
    save_image(DIR_RESULTS_MASK + "star_reduced.png", star_reduced, cmap="gray")
    return star_reduced


def combinate_mask_image(image_starless, image_starreduced):
    """
    Combinate the mask with the erodedImage and the origin image

    :param mask: the mask
    :param imgEroded: the eroded image
    :param image_origin: the origin image convert in grey
    """
    final_image = image_starless + image_starreduced
    save_image(
        DIR_RESULTS_FINAL + "final_combined_phase3.png", final_image, cmap="gray"
    )
    final_fit = fits.writeto(
        DIR_RESULTS_FINAL + "final_combined_phase3.fits",
        final_image,
        header_starless,
        overwrite=True,
    )
    return final_image, final_fit


if __name__ == "__main__":
    """
    The objective is to recuperate two pictures from StarNet :
     - a starless picture
     - a staronly picture
    Then, we create a mask from the staronly picture with a threshold
    We apply effects on the mask (dilation and gaussian blur)
    We reduce the staronly picture with the mask
    Wee combine the starless picture and the reduced staronly picture to obtain a final
    """
    # Load starless file and starfile
    starless_file = "/home/valentin/astro/star_reduction/starless_test_M31_linear.fit"
    staronly_file = "/home/valentin/astro/star_reduction/starmask_test_M31_linear.fit"

    # Load starless and apply handler_color_image for normalization
    data_starless, header_starless = load_fits(starless_file)
    starless = handler_color_image(data_starless)

    # Load staronly and apply handler_color_image for normalization
    data_staronly, header_staronly = load_fits(staronly_file)
    staronly = handler_color_image(data_staronly)

    # Save original images loaded
    save_image(DIR_RESULTS_ORIGINAL + "starless.png", starless)
    save_image(DIR_RESULTS_ORIGINAL + "staronly.png", staronly)

    # Convert in grey
    staronly_gray = convert_in_grey(staronly)
    starless_file_gray = convert_in_grey(starless)

    # Create mask from staronly image
    mask = mask_from_stars_starnet(staronly_gray, thresh=0.05)

    # Apply Gaussian Blur
    maskFlouGaussien = mask_effects(mask, (3, 3), (3, 3), iterations=1)

    # Reduce staronly image with the mask and alpha factor
    star_reduced = reduce_stars(staronly_gray, maskFlouGaussien, alpha=0.8)

    # Combine starless image and reduced staronly image
    final, final_fit = combinate_mask_image(starless_file_gray, star_reduced)

    # Debug datatype
    print("============= check of datatype ===================")
    print("starless_file_gray.dtype:", starless_file_gray.dtype)
    print("star_reduced.dtype:", star_reduced.dtype)
    print("final.dtype:", final.dtype)
