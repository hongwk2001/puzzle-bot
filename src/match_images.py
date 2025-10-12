import os
import numpy as np
import math
import shutil

from common.util import load_bmp_as_binary_pixels
from common import util, sides, vector
from common.config import *

# From dedupe.py
SIDE_MISALIGNMENT_RAD = 12.0 * math.pi / 180
GEOMETRIC_SIMILARITY_THRESHOLD = 2.2

def remove_small_images(directory, min_pixels=1000):
    """
    Removes images from a directory that are smaller than a specified pixel area.
    """
    print(f"Scanning for small images in: {directory}")
    image_files = [f for f in os.listdir(directory) if f.endswith('.bmp')]
    removed_count = 0
    for filename in image_files:
        path = os.path.join(directory, filename)
        try:
            _, width, height = load_bmp_as_binary_pixels(path)
            if width * height < min_pixels:
                os.remove(path)
                print(f"Removed small image: {filename} ({width}x{height})")
                removed_count += 1
        except Exception as e:
            print(f"Could not process {filename}: {e}")
    if removed_count > 0:
        print(f"Removed {removed_count} small images.")
    else:
        print("No small images found to remove.")

def get_sides_from_image(path, id, debug=False, debug_dir=None):
    """
    Processes an image file and returns its four sides, resampled for comparison.
    """
    try:
        v = vector.Vector.from_file(path, id)
        v.find_border_raster()
        v.vectorize()
        v.find_four_corners()
        v.extract_four_sides()
        v.enhance_corners()

        if debug and debug_dir:
            v.save(debug_dir, metadata={'source_file': os.path.basename(path)})

        if len(v.sides) != 4:
            return None

        resampled_sides = []
        for side in v.sides:
            resampled_side = sides.Side(
                piece_id=side.piece_id, side_id=side.side_id, vertices=side.vertices,
                piece_center=side.piece_center, is_edge=side.is_edge,
                resample=True, rotate=True
            )
            resampled_sides.append(resampled_side)
        return resampled_sides

    except Exception:
        return None

def compare_pieces(sides0, sides1, debug=False):
    """
    Compare two pieces, returning a score of how similar they are (lower is better).
    """
    if not sides0 or not sides1:
        return 1000

    permutations = [sides0[i:] + sides0[:i] for i in range(4)]

    min_cumulative_error = 1000
    for p_sides0 in permutations:
        cumulative_error = sum(
            p_sides0[i].error_when_fit_with(sides1[i], flip=False, skip_edges=False, render=debug)
            for i in range(4)
        )
        if cumulative_error < min_cumulative_error:
            min_cumulative_error = cumulative_error

    return min_cumulative_error

def deduplicate_images(directory):
    """
    Finds all groups of duplicate images and prints a summary.
    """
    image_files = [f for f in os.listdir(directory) if f.endswith('.bmp')]
    image_sides_cache = {}

    print(f"\nProcessing {len(image_files)} images to extract sides...")
    for i, filename in enumerate(image_files):
        path = os.path.join(directory, filename)
        sides_data = get_sides_from_image(path, i)
        if sides_data:
            image_sides_cache[filename] = sides_data
        print(f" {i+1}/{len(image_files)}", end='\r')

    uniques = {}
    processed_files = set()
    files_to_check = list(image_sides_cache.keys())

    print("\nDeduplicating images...")
    for i, file1 in enumerate(files_to_check):
        if file1 in processed_files:
            continue

        # This is a new unique piece
        uniques[file1] = []
        processed_files.add(file1)

        for j in range(i + 1, len(files_to_check)):
            file2 = files_to_check[j]
            if file2 in processed_files:
                continue

            sides1 = image_sides_cache[file1]
            sides2 = image_sides_cache[file2]

            score = compare_pieces(sides1, sides2)

            if score < GEOMETRIC_SIMILARITY_THRESHOLD:
                uniques[file1].append(file2)
                processed_files.add(file2)

    print("\n--- Deduplication Summary ---")
    if not uniques:
        print("No images processed.")
        return

    for unique_file, duplicate_files in uniques.items():
        if duplicate_files:
            print(f"\nUnique Piece: {unique_file}")
            for dupe in duplicate_files:
                print(f"  - Duplicate: {dupe}")

    print(f"\nTotal unique pieces found: {len(uniques)}")

def find_matches_for_image(directory, image_filename):
    """
    Finds and prints matches for a specific image in a directory.
    """
    target_path = os.path.join(directory, image_filename)
    if not os.path.exists(target_path):
        print(f"Target image not found: {image_filename}")
        return

    print(f"\nFinding matches for: {image_filename}")
    target_sides = get_sides_from_image(target_path, "target")
    if not target_sides:
        print(f"Could not process target image: {image_filename}")
        return

    image_files = [f for f in os.listdir(directory) if f.endswith('.bmp') and f != image_filename]
    found_match = False

    for i, filename in enumerate(image_files):
        path = os.path.join(directory, filename)
        sides_to_compare = get_sides_from_image(path, i)
        if not sides_to_compare:
            continue

        score = compare_pieces(target_sides, sides_to_compare)

        if score < GEOMETRIC_SIMILARITY_THRESHOLD:
            print(f"  - Found match: {filename} (score: {score:.2f}) {i} {target_sides}")
            found_match = True

    if not found_match:
        print("  - No matches found.")

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    segmented_dir = os.path.join(project_root, 'example_data', '2_segmented')

    # Remove small images before matching
    #remove_small_images(segmented_dir)

    # Find matches for a specific image
    image_to_find_matches_for = '20240603_172450_(1210,338).bmp'
    find_matches_for_image(segmented_dir, image_to_find_matches_for)
