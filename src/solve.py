"""
Given a path to processed piece data, finds a solution
"""

import os
import time

from common import board, connect, util, move, spacing
from common.config import *


def solve(path, start_at=3):
    """
    Given a path to processed piece data, finds a solution
    """
    if start_at <= 5:
        connectivity = _find_connectivity(input_path=os.path.join(path, DEDUPED_DIR), output_path=os.path.join(path, CONNECTIVITY_DIR))
    else:
        connectivity = None

    """
    [[[4, 3], [3, 2], 0.3898767906588657],
     [[4, 0], [2, 2], 0.4220842274523208],
     [[1, 0], [3, 2], 0.6361147637065704],
     [[3, 1], [2, 2], 1.0327136935635464],
     [[2, 3], [4, 3], 1.1649732899984064]] """

    # step 6 ( new ) - pick best 3 and Express as image
    if start_at <= 6 :
        #pick  best 3
        best_connectivity = connectivity[0:3]
        _visualize(best_connectivity,
                   os.path.join(path, PHOTOS_DIR),
                   os.path.join(path, CONNECTIVITY_DIR),
                   os.path.join(path, SOLUTION_DIR, "top3_connectivity.png"))

    # Step 5.2 - build the board  not 6, kinda messed up the numbering

def _visualize(connectivity, photos_path, conn_path, solution_path, file_name="connectivity.png"):
    """
    Visualizes the connectivity as an image
    """
    print(f"\n{util.BLUE}### Step 6 - pick best 3  Visualizing connectivity ###{util.WHITE}\n")
    start_time = time.time()

    import cv2
    import numpy as np

    # Load an example image (make sure the path is correct)
    image = cv2.imread(os.path.join(PHOTOS_DIR, r"20251012_1.jpg"))

    for c in connectivity:
        print(c)
        # get points from svg

        arrow1_start = (50, 50)
        arrow1_end = (200, 100)
        # Draw the arrows on the image
        # cv2.arrowedLine(image, start_point, end_point, color, thickness, tipLength)
        cv2.arrowedLine(image, arrow1_start, arrow1_end, color=(255, 0, 0), thickness=2, tipLength=0.1)  # Blue arrow

    # Save or show the image
    cv2.imwrite("arrows_example_opencv.png", image)
    print("Image with arrows saved as 'arrows_example_opencv.png'")

    duration = time.time() - start_time
    print(f"Visualizing the graph took {round(duration, 2)} seconds")

def _find_connectivity(input_path, output_path):
    """
    Opens each piece data and finds how each piece could connect to others
    """
    print(f"\n{util.BLUE}### Step 5.1- Building connectivity ###{util.WHITE}\n")
    start_time = time.time()
    connectivity = connect.build(input_path, output_path)
    duration = time.time() - start_time
    print(f"Building the graph took {round(duration, 2)} seconds")
    return connectivity
