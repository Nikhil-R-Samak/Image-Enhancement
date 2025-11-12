import os
import subprocess
import sys
import uuid
from PIL import Image

class ImageEnhancer:
    def __init__(
        self,
        realesrgan_script="inference_realesrgan.py",
        tile_size=1024,
        overlap=0
    ):
        self.realesrgan_script = realesrgan_script
        self.tile_size = tile_size
        self.overlap = overlap

    def _run_realesrgan(self, tile_path,scale):
        """Run Real-ESRGAN on a single tile using subprocess."""
        print(f"Enhancing {os.path.basename(tile_path)} with scale {scale}x...")
        subprocess.run([
            sys.executable, self.realesrgan_script,
            "-i", tile_path,
            "--outscale", str(scale)
        ], check=True)

    def _get_tile_coordinates(self, filename):
        """Extract (x, y) from filenames like tile_1024_2048_out.png."""
        name = filename.replace(".png", "").replace("tile_", "").replace("_out", "")
        x_str, y_str = name.split("_")
        return int(x_str), int(y_str)

    def _split_image(self, image_path, tiles_dir):
        """Split input image into tiles and save them."""
        os.makedirs(tiles_dir, exist_ok=True)
        image = Image.open(image_path)
        width, height = image.size

        tile_paths = []
        for y in range(0, height, self.tile_size - self.overlap):
            for x in range(0, width, self.tile_size - self.overlap):
                box = (x, y, min(x + self.tile_size, width), min(y + self.tile_size, height))
                tile = image.crop(box)
                tile_filename = f"tile_{x}_{y}.png"
                tile_path = os.path.join(tiles_dir, tile_filename)
                tile.save(tile_path)
                tile_paths.append(tile_path)

        print(f"Split into {len(tile_paths)} tiles.")
        return tile_paths

    def _merge_tiles(self, results_dir, output_path, scale):
        """Merge enhanced tiles back into one high-resolution image."""
        tile_files = [f for f in os.listdir(results_dir) if f.endswith("_out.png")]
        if not tile_files:
            raise FileNotFoundError("No enhanced tiles found in results directory.")

        tiles = []
        max_x = max_y = 0
        for filename in tile_files:
            x, y = self._get_tile_coordinates(filename)
            path = os.path.join(results_dir, filename)
            tile = Image.open(path)

            x_scaled = x * scale
            y_scaled = y * scale
            tiles.append((tile, (x_scaled, y_scaled)))

            max_x = max(max_x, x_scaled + tile.width)
            max_y = max(max_y, y_scaled + tile.height)

        print(f"Merging {len(tiles)} tiles → {max_x}x{max_y}")
        result_image = Image.new('RGB', (max_x, max_y))
        for tile, (x, y) in tiles:
            result_image.paste(tile, (x, y))

        result_image.save(output_path)
        print(f"Final merged image saved at: {output_path}")
        return output_path

    def enhance(self, image_path, scale = 2):
        """
        Full pipeline: Split → Enhance (RealESRGAN) → Merge.
        Returns path to final enhanced image.
        """
        session_id = str(uuid.uuid4())[:8]
        base_dir = os.path.join("saved_results", session_id)
        tiles_dir = os.path.join(base_dir, "tiles_output")
        results_dir = "results"  # Real-ESRGAN outputs enhanced tiles here
        final_path = os.path.join(base_dir, "final_enhanced.png")

        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)

        # 1️⃣ Split
        tile_paths = self._split_image(image_path, tiles_dir)

        # 2️⃣ Enhance each tile
        for tile_path in tile_paths:
            try:
                self._run_realesrgan(tile_path,scale)
            except subprocess.CalledProcessError as e:
                print(f"Error processing {tile_path}: {e}")

        # 3️⃣ Merge
        return self._merge_tiles(results_dir, final_path,scale)