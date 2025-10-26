import time
from PIL import Image
from typing import List, Tuple
from pathlib import Path

from common import util
from common.config import *


def photo_to_bmp(args):
    input_photo_filename, output_bmp_filename = args
    return segment(input_photo_filename, output_bmp_filename)

def rembg_remove(input_photo_filepath: str) -> Path:
    model_path = Path(__file__).parent / "isnet_dis.onnx"

    input_path = Path(input_photo_filepath)
    try:
        with Image.open(input_photo_filepath) as input_image:
            try:
                from dis_bg_remover import remove_background
            except Exception as e:
                raise RuntimeError("background remover not available") from e

            #verify model file exists
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found at {model_path}")

            extracted_img_np, mask_np = remove_background(str(model_path), str(input_photo_filepath))

            if extracted_img_np is None:
                raise Exception("extracted_img_np is None")

            import numpy as np
            # ensure uint8 [0,255]
            if extracted_img_np.dtype != np.uint8:
                extracted_img_np = (extracted_img_np * 255).astype("uint8")
            if mask_np.dtype != np.uint8:
                mask_np = (mask_np * 255).astype("uint8")

            extracted_img = Image.fromarray(extracted_img_np)
            output_img = Image.fromarray(mask_np)

            extracted_img_filepath = input_path.with_name(f"{input_path.stem}_extracted.png")
            extracted_img.save(extracted_img_filepath)

            output_img_filepath = input_path.with_name(f"{input_path.stem}_out.png")
            output_img.save(output_img_filepath)

            return output_img_filepath
            #return extracted_img_filepath
    except Exception as e:
        print(f"rembg_remove failed for {input_photo_filepath}: {e}")
        raise

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
