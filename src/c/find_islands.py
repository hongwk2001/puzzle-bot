
import os
import sys
from PIL import Image
from multiprocessing import Pool, cpu_count

class Island:
    """Represents a single island found in the grid."""
    def __init__(self, min_x, max_x, min_y, max_y):
        padding = 1
        self.rows = max_x - min_x + 1 + (2 * padding)
        self.cols = max_y - min_y + 1 + (2 * padding)
        self.origin_x = min_x - padding
        self.origin_y = min_y - padding
        self.matrix = [[0] * self.cols for _ in range(self.rows)]

def _is_straggler(mat, x, y, rows, cols):
    """Checks if a pixel is a 'straggler' with 2 or fewer neighbors."""
    neighbors = 0
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and mat[nx][ny] == 1:
                neighbors += 1
    return neighbors <= 2

def remove_stragglers(matrix, rows, cols):
    """
    Removes isolated or weakly connected pixels (stragglers) from the grid.
    This is a pre-processing step to clean up noise.
    """
    i = 1
    while i < rows - 1:
        j = 1
        while j < cols - 1:
            if matrix[i][j] == 1 and _is_straggler(matrix, i, j, rows, cols):
                matrix[i][j] = 0
                # Backtrack to re-check the area in case removing this pixel
                # created a new straggler.
                i = max(1, i - 2)
                j = max(1, j - 2)
            j += 1
        i += 1
    return matrix

def mark_island(grid, rows, cols, x, y, visited, island_id):
    """
    Finds all connected parts of an island starting from (x, y) using an
    iterative Depth-First Search (DFS).
    """
    if not (0 <= x < rows and 0 <= y < cols and grid[x][y] == 1 and visited[x][y] == 0):
        return None

    stack = [(x, y)]
    min_x, max_x = x, x
    min_y, max_y = y, y
    area = 0

    while stack:
        px, py = stack.pop()

        if not (0 <= px < rows and 0 <= py < cols and grid[px][py] == 1 and visited[px][py] == 0):
            continue

        visited[px][py] = island_id
        area += 1
        min_x, max_x = min(min_x, px), max(max_x, px)
        min_y, max_y = min(min_y, py), max(max_y, py)

        # Push neighbors onto the stack
        stack.append((px + 1, py))
        stack.append((px - 1, py))
        stack.append((px, py + 1))
        stack.append((px, py - 1))

    return area, min_x, max_x, min_y, max_y

def find_islands(grid, rows, cols, min_island_area, ignore_islands_along_border):
    """
    Finds all islands in a grid that meet the specified criteria.
    """
    visited = [[0] * cols for _ in range(rows)]
    islands = []
    island_id = 1

    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 1 and visited[i][j] == 0:
                result = mark_island(grid, rows, cols, i, j, visited, island_id)
                if not result:
                    continue

                area, min_x, max_x, min_y, max_y = result
                on_border = (min_x == 0 or max_x == rows - 1 or min_y == 0 or max_y == cols - 1)

                if area >= min_island_area and not (ignore_islands_along_border and on_border):
                    new_island = Island(min_x, max_x, min_y, max_y)
                    for r in range(min_x, max_x + 1):
                        for c in range(min_y, max_y + 1):
                            if visited[r][c] == island_id:
                                new_island.matrix[r - min_x + 1][c - min_y + 1] = 1
                    islands.append(new_island)
                
                island_id += 1
    
    return islands

def save_island_as_bmp(island, filename):
    """Saves an Island object as a 1-bit monochrome BMP file."""
    img = Image.new('1', (island.cols, island.rows), 0)
    pixels = img.load()
    for r in range(island.rows):
        for c in range(island.cols):
            if island.matrix[r][c] == 1:
                pixels[c, r] = 1
    img.save(filename)

def extract_from_file(filepath, filename, output_dir, min_island_area):
    """
    Main processing function for a single file.
    """
    print(f"Extracting from {filepath}")
    try:
        with Image.open(filepath) as img:
            # Ensure image is 1-bit monochrome
            img = img.convert('1')
            width, height = img.size
            
            # Convert image to a list of lists (grid)
            grid = [[img.getpixel((c, r)) for c in range(width)] for r in range(height)]
            
            # In Pillow, white is 255 and black is 0. The C code looks for islands of 1s.
            # In a typical monochrome BMP, 1 is white. So we should treat non-black pixels as the island.
            grid = [[1 if pixel != 0 else 0 for pixel in row] for row in grid]

    except Exception as e:
        print(f"Error: Unable to open or process file {filepath}. Reason: {e}")
        return

    # 1. Pre-process the image to remove stragglers
    grid = remove_stragglers(grid, height, width)

    # 2. Find all large islands that don't touch the border
    ignore_islands_along_border = True
    islands = find_islands(grid, height, width, min_island_area, ignore_islands_along_border)

    # 3. Save each island as a separate BMP file
    base_filename = os.path.splitext(filename)[0]
    for i, island in enumerate(islands):
        output_filename = os.path.join(
            output_dir,
            f"{base_filename}_({island.origin_y},{island.origin_x}).bmp"
        )
        save_island_as_bmp(island, output_filename)

def process_file_worker(args):
    """Helper function to unpack arguments for the worker pool."""
    filepath, filename, output_dir, min_island_area = args
    extract_from_file(filepath, filename, output_dir, min_island_area)

def main():
    """
    Main function to handle command-line arguments and orchestrate the
    file processing using a multiprocessing pool.
    """
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <input_directory> <output_directory> <min_island_area>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    min_island_area = int(sys.argv[3])

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory not found at {input_dir}")
        sys.exit(1)
        
    if not os.path.isdir(output_dir):
        print(f"Error: Output directory not found at {output_dir}")
        sys.exit(1)

    # Create a list of tasks
    tasks = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".bmp"):
            filepath = os.path.join(input_dir, filename)
            tasks.append((filepath, filename, output_dir, min_island_area))

    # Use a process pool to execute tasks in parallel
    # Uses a sensible number of workers, but not more than MAX_THREADS from the C code
    num_workers = min(cpu_count(), 14)
    with Pool(processes=num_workers) as pool:
        pool.map(process_file_worker, tasks)

    print("Processing complete.")

if __name__ == "__main__":
    main()
