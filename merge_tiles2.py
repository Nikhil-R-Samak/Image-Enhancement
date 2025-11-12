# import os
# import argparse
# from PIL import Image

# def get_tile_coordinates(filename):
#     """
#     Extract (x, y) from filenames like tile_1024_2048_out.png
#     """
#     name = filename.replace(".png", "").replace("tile_", "").replace("_out", "")
#     x_str, y_str = name.split("_")
#     return int(x_str), int(y_str)

# def merge_tiles(tile_dir, output_path):
#     tile_files = [f for f in os.listdir(tile_dir) if f.endswith("_out.png")]

#     if not tile_files:
#         print("No tile images found in the directory.")
#         return

#     tiles = []
#     max_x = max_y = 0

#     # Collect tile images and their positions
#     for filename in tile_files:
#         x, y = get_tile_coordinates(filename)
#         path = os.path.join(tile_dir, filename)
#         tile = Image.open(path)
#         tiles.append((tile, (x, y)))
#         max_x = max(max_x, x + tile.width)
#         max_y = max(max_y, y + tile.height)

#     print(f"Total tiles: {len(tiles)}")
#     print(f"Final image size: {max_x} x {max_y}")

#     # Create blank image
#     result_image = Image.new('RGB', (max_x, max_y))

#     # Paste each tile into final image
#     for tile, (x, y) in tiles:
#         result_image.paste(tile, (x, y))

#     # Save final image
#     result_image.save(output_path)
#     print(f"Merged image saved to: {output_path}")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Merge Real-ESRGAN output tiles into one image.")
#     parser.add_argument("--input", required=True, help="Path to folder with tiles (e.g., Real-ESRGAN results).")
#     parser.add_argument("--output", default="merged_output.png", help="Path to save merged image.")

#     args = parser.parse_args()

#     merge_tiles(args.input, args.output)

# """
# python merge_tiles.py --input "C:\Users\GuestUser\Real-ESRGAN\results" --output "C:\Users\GuestUser\Real-ESRGAN\merged_image.png"

# """

import os
import argparse
from PIL import Image

SCALE = 2  # must match your --outscale value in split_and_process.py

def get_tile_coordinates(filename):
    """
    Extract (x, y) from filenames like tile_1024_2048_out.png
    """
    name = filename.replace(".png", "").replace("tile_", "").replace("_out", "")
    x_str, y_str = name.split("_")
    return int(x_str), int(y_str)

def merge_tiles(tile_dir, output_path, scale=SCALE):
    tile_files = [f for f in os.listdir(tile_dir) if f.endswith("_out.png")]

    if not tile_files:
        print("No tile images found in the directory.")
        return

    tiles = []
    max_x = max_y = 0

    # Collect tile images and their positions
    for filename in tile_files:
        x, y = get_tile_coordinates(filename)
        path = os.path.join(tile_dir, filename)
        tile = Image.open(path)

        # Scale coordinates so tiles align correctly
        x_scaled = x * scale
        y_scaled = y * scale

        tiles.append((tile, (x_scaled, y_scaled)))
        max_x = max(max_x, x_scaled + tile.width)
        max_y = max(max_y, y_scaled + tile.height)

    print(f"Total tiles: {len(tiles)}")
    print(f"Final image size: {max_x} x {max_y}")

    # Sort tiles first by Y, then by X
    tiles.sort(key=lambda t: (t[1][1], t[1][0]))

    # Create blank image
    result_image = Image.new('RGB', (max_x, max_y))

    # Paste each tile into final image
    for tile, (x, y) in tiles:
        result_image.paste(tile, (x, y))

    # Save final image
    result_image.save(output_path)
    print(f"Merged image saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge Real-ESRGAN output tiles into one image.")
    parser.add_argument("--input", required=True, help="Path to folder with tiles (e.g., Real-ESRGAN results).")
    parser.add_argument("--output", default="merged_output.png", help="Path to save merged image.")
    parser.add_argument("--scale", type=int, default=SCALE, help="Upscale factor used in Real-ESRGAN (e.g., 2, 3, 4).")

    args = parser.parse_args()

    merge_tiles(args.input, args.output, args.scale)

