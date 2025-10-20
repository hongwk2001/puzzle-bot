"""
Given a path to processed piece data, finds a solution
"""

import os
import time
import json
import cv2
from PIL import Image

import numpy as np
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
        fr_p_ctr = np.array(from_data["photo_space_centroid"])
        fr_piece_center = np.array(from_data["piece_center"])
        fr_vertices = np.array(from_data["vertices"])
        fr_first_vertex = fr_vertices[0]
        fr_last_vertex = fr_vertices[-1]

        fr_first_edge = fr_p_ctr - fr_piece_center + fr_first_vertex
        fr_last_edge = fr_p_ctr - fr_piece_center + fr_last_vertex
        # find center points between edges
        fr_edge_ctr = (fr_last_edge + fr_first_edge) // 2

        with open(to_piece_side_json_path, 'r') as f:
            to_data = json.load(f)
        to_p_ctr = np.array(to_data["photo_space_centroid"])
        to_piece_center = np.array(to_data["piece_center"])
        to_vertices = np.array(to_data["vertices"])
        to_first_vertex = to_vertices[0]
        to_last_vertex = to_vertices[-1]

        to_last_edge = to_p_ctr - to_piece_center + to_last_vertex
        to_first_edge = to_p_ctr - to_piece_center + to_first_vertex
        # find center points between edges
        to_edge_ctr = (to_first_edge + to_last_edge) // 2

        # Draw the arrows on the image
        # Use a different color for each arrow, cycling through the colors list
        color = colors[i % len(colors)]

        #draw a line from fr_first_edge to fr_last_edge
        cv2.line(image, tuple(fr_first_edge.astype(int)), tuple(fr_last_edge.astype(int)), color=color, thickness=20)
        cv2.line(image, tuple(to_first_edge.astype(int)), tuple(to_last_edge.astype(int)), color=color, thickness=20)
        cv2.arrowedLine(image, tuple(fr_edge_ctr.astype(int)), tuple(to_edge_ctr.astype(int)), color, 20, tipLength=0.05)

    # save image
    solution_file_path = os.path.join(path, SOLUTION_DIR, "top3_connectivity.png")
    cv2.imwrite(solution_file_path, image)
    print(f"Image with arrows saved as '{solution_file_path}'")

    duration = time.time() - start_time
    print(f"Visualizing the graph took {round(duration, 2)} seconds")

    #show image
    Image.open(solution_file_path).show()

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
