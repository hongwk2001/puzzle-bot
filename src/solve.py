"""
Given a path to processed piece data, finds a solution
"""

import os
import time
import json
import cv2

from common import connect, util
from common.config import *


def solve(path, start_at=3):
    """
    Given a path to processed piece data, finds a solution
    """
    if start_at <= 5:
        connectivity = _find_connectivity(input_path=os.path.join(path, DEDUPED_DIR),
                                          output_path=os.path.join(path, CONNECTIVITY_DIR))
    else:
        connectivity = None

    # step 6 ( new ) - pick best 3 and Express as image
    if start_at <= 6:
        # pick  best 3
        if connectivity:
            best_connectivity = connectivity[0:3]
            _visualize(best_connectivity, path)

    # Step 5.2 - build the board  not 6, kinda messed up the numbering


def _visualize(connectivity, path):
    """
    Visualizes the connectivity as an image
    """
    print(f"\n{util.BLUE}### Step 6 - pick best 3  Visualizing connectivity ###{util.WHITE}\n")
    start_time = time.time()

    # Load an example image (make sure the path is correct)
    # I'll have only one photo , so not too wrong
    # let's come back. BH
    image = cv2.imread(os.path.join(path, PHOTOS_DIR, r"20251012_1.jpg"))

    # BGR colors for the arrows
    colors = [
        (255, 0, 0),    # Blue
        (0, 255, 0),    # Green
        (0, 0, 255),    # Red
    ]

    for i, c in enumerate(connectivity):
        print(c)
        # [[4, 3], [3, 2], 0.3898767906588657]
        from_piece_side, to_piece_side = c[0], c[1]
        # get points from json files
        side_path = os.path.join(path, DEDUPED_DIR)
        from_piece_side_json_path = os.path.join(side_path, f"side_{from_piece_side[0]}_{from_piece_side[1]}.json")
        to_piece_side_json_path = os.path.join(side_path, f"side_{to_piece_side[0]}_{to_piece_side[1]}.json")

        with open(from_piece_side_json_path, 'r') as f:
            from_data = json.load(f)
        from_points = from_data["photo_space_centroid"]

        with open(to_piece_side_json_path, 'r') as f:
            to_data = json.load(f)
        to_points = to_data["photo_space_centroid"]

        arrow1_start = tuple(int(x) for x in from_points)
        arrow1_end = tuple(int(x) for x in to_points)

        # Draw the arrows on the image
        # Use a different color for each arrow, cycling through the colors list
        color = colors[i % len(colors)]
        # cv2.arrowedLine(image, start_point, end_point, color, thickness, tipLength)
        cv2.arrowedLine(image, arrow1_start, arrow1_end, color=color, thickness=5, tipLength=0.1)

    # save image
    solution_file_path = os.path.join(path, SOLUTION_DIR, "top3_connectivity.png")
    cv2.imwrite(solution_file_path, image)
    print(f"Image with arrows saved as '{solution_file_path}'")

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
