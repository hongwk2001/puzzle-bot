import os
import re
import pathlib
from multiprocessing import Pool, cpu_count

from .config import *
from c import find_islands as island_finder


def batch_extract(input_path, output_path, scale_factor):
    input_path = pathlib.Path(input_path)
    output_path = pathlib.Path(output_path)

    print(f"Extracting islands from BMPs in {input_path} to {output_path}")

    tasks = []
    for filename in os.listdir(input_path):
        if filename.lower().endswith(".bmp"):
            filepath = os.path.join(input_path, filename)
            tasks.append((filepath, filename, str(output_path), MIN_PIECE_AREA))

    # Use a process pool to execute tasks in parallel
    # Uses a sensible number of workers, but not more than MAX_THREADS from the C code
    num_workers = min(cpu_count(), 14)
    with Pool(processes=num_workers) as pool:
        pool.map(island_finder.process_file_worker, tasks)

    print("Island extraction complete.")

    output_photo_space_positions = {}

    fs = [f for f in os.listdir(output_path) if f.endswith('.bmp')]
    for f in fs:
        components = f.split('.')[0].split('_')
        origin_component = components[-1]
        origin_x, origin_y = origin_component.strip('(').strip(')').split(',')
        origin = (int(origin_x), int(origin_y))

        photo_space_position = (origin[0] / scale_factor + CROP_TOP_RIGHT_BOTTOM_LEFT[-1], origin[1] / scale_factor + CROP_TOP_RIGHT_BOTTOM_LEFT[0])
        output_photo_space_positions[f] = photo_space_position
        print(f"Extracted {f} at {photo_space_position}, origin {origin}")

    return output_photo_space_positions
