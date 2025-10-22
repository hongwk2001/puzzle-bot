import time
from PIL import Image
from typing import List, Tuple
from pathlib import Path

from common import util
from common.config import *


def photo_to_bmp(args):
    input_photo_filename, output_bmp_filename = args
    return segment(input_photo_filename, output_bmp_filename)

def  rembg_remove(input_photo_filepath):

    input_image = Image.open(input_photo_filepath)
    input_path = Path(input_photo_filepath)

    # Remove the background
    from rembg import remove
    output_image = remove(input_image) # type: ignore
    #output_image.show('Removed Background')
    output_image.save(input_path.with_name(f'{input_path.stem}_removed.png')) # type: ignore

    # Extract the alpha channel to create a black and white mask
    # The alpha channel is an 'L' mode image where the background is black (0)
    # and the foreground is white (255).
    output_image = output_image.getchannel('A')
    #output_image.show('Alpha Channel Mask')
    output_image.save(input_path.with_name(f'{input_path.stem}_alpha.png')) # type: ignore

    # Save the output image
    #output_image.show('Morphology Applied')
    output_image_filepath = input_path.with_name(f'{input_path.stem}_out.jpg')
    output_image.save(input_path.with_name(f'{input_path.stem}_out.jpg')) # type: ignore
    return output_image_filepath

def segment(input_photo_filepath, output_path=None, width=SCALE_BMP_TO_WIDTH, threshold=SEG_THRESH, crop=CROP_TOP_RIGHT_BOTTOM_LEFT):
    """
    Takes in a photo of one or more puzzle pieces
    Generates a binary image that is slightly cleaned up
    Removes dust and debris from the image
    Scales the binary image by the provided factor

    If an output path is provided, this function saves the resulting bitmap
    Returns the pixels and dimensions

    width: the maximum width of the output image
    white_pieces: whether the pieces are white on a black background (True) or black on a white background (False)
    threshold: the threshold for the binary image
    clean: whether to clean up the image iwth some post-processing
    """

    print(f"> Segmenting photo `{input_photo_filepath}` into `{output_path}`")
    removed_image_filepath = rembg_remove(input_photo_filepath)

    bw_pixels, width, height, scale_factor = util.binary_pixel_data_for_photo(removed_image_filepath ,
                                                                              threshold=threshold, max_width=width,
                                                                              crop=crop)
    if output_path:
        _save(output_path, bw_pixels, width, height)

    return width, height, scale_factor


def _save(output_path, bw_pixels, width, height):
    img = Image.new('1', (width, height))
    img.putdata([pixel for row in bw_pixels for pixel in row])
    img.save(output_path)
