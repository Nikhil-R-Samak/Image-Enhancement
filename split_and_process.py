import os
import argparse
import subprocess
from PIL import Image
import sys

def split_and_process(image_path, output_dir, tile_size=1024, overlap=0, realesrgan_script='inference_realesrgan.py'):
    os.makedirs(output_dir, exist_ok=True)
    image = Image.open(image_path)
    width, height = image.size

    tile_id = 0
    for y in range(0, height, tile_size - overlap):
        for x in range(0, width, tile_size - overlap):
            box = (x, y, min(x + tile_size, width), min(y + tile_size, height))
            tile = image.crop(box)

            # Save tile
            tile_filename = f"tile_{x}_{y}.png"
            tile_path = os.path.join(output_dir, tile_filename)
            tile.save(tile_path)

            # Call Real-ESRGAN subprocess
            print(f"Processing tile: {tile_filename}")
            try:
                subprocess.run([
                    sys.executable, realesrgan_script,
                    "-n", "RealESRGAN_x4plus",
                    "-i", tile_path,
                    "--outscale", "2"
                ], check=True)

                # Assuming Real-ESRGAN saves as same name (or you can adjust this if different)
                # You can delete the original tile if needed
                # os.remove(tile_path)
            except subprocess.CalledProcessError as e:
                print(f"Error processing tile {tile_filename}: {e}")

            tile_id += 1

    print(f"Done! {tile_id} tiles processed and saved in: {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split and process image tiles with Real-ESRGAN.")
    parser.add_argument("--input", required=True, help="Path to the input image.")
    parser.add_argument("--output", default="tiles_output", help="Directory to save tiles.")
    parser.add_argument("--tile_size", type=int, default=1024, help="Tile size for splitting.")
    parser.add_argument("--overlap", type=int, default=0, help="Overlap between tiles.")
    parser.add_argument("--realesrgan_script", default="inference_realesrgan.py", help="Path to the Real-ESRGAN script.")

    args = parser.parse_args()

    split_and_process(args.input, args.output, args.tile_size, args.overlap, args.realesrgan_script)
