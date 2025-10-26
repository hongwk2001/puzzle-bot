from rembg import remove
from PIL import Image, ImageFilter
import os
from pathlib import Path
import cv2
import numpy as np

#from google_contoure import output_filename

# Define input and output paths
input_path = Path(r'..\dora_24pieces\0_photos\hidden_from_code\20251015_085736.jpg')  # Replace with your input image file
#get file name from input path

# Open the input image
input_image = Image.open(input_path)

# Remove the background
output_image = remove(input_image)
output_image.show('Removed Background')
output_image.save(input_path.with_name(f'{input_path.stem}_removed.png'))

# Extract the alpha channel to create a black and white mask
# The alpha channel is an 'L' mode image where the background is black (0)
# and the foreground is white (255).
output_image = output_image.getchannel('A')
output_image.show('Alpha Channel Mask')
output_image.save(input_path.with_name(f'{input_path.stem}_alpha.png'))

# Save the output image
output_image.show('Morphology Applied')
output_image.save(input_path.with_name(f'{input_path.stem}_out.jpg'))
