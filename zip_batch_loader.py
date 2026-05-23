"""
Core logic for the ComfyUI ZIP Batch Loader custom node.
"""

import io
import logging
import os
import zipfile

import numpy as np
import torch  # pylint: disable=import-error
from PIL import Image

import folder_paths  # pylint: disable=import-error


class ZipBatchLoader:
    """
    A custom node to load a batch of images directly from a ZIP archive.
    """

    @classmethod
    def INPUT_TYPES(cls):  # pylint: disable=invalid-name
        """Defines the input types for the ComfyUI node."""
        files = []
        try:
            input_dir = folder_paths.get_input_directory()
            files = [
                f
                for f in os.listdir(input_dir)
                if os.path.isfile(os.path.join(input_dir, f)) and f.lower().endswith(".zip")
            ]
        except OSError as e:
            logging.error("[ZipBatchLoader] Failed to read input directory: %s", e)

        return {
            "required": {
                "zip_file": (files,),
                "heterogeneous_dimensions": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT")
    RETURN_NAMES = ("image", "mask", "count")
    FUNCTION = "load_from_zip"
    CATEGORY = "image"

    def _process_image_file(self, archive, filename, first_dims, heterogeneous_dims):
        """Helper to process a single image from the archive."""
        with archive.open(filename) as file_obj:
            try:
                img = Image.open(io.BytesIO(file_obj.read()))
                img.load()  # Force load the image data
            except OSError as e:
                logging.warning("Failed to load image %s: %s", filename, e)
                return None, None, first_dims

            if first_dims is None:
                first_dims = img.size
            elif img.size != first_dims:
                if not heterogeneous_dims:
                    raise ValueError(
                        f"Dimension mismatch: {filename} has dimensions "
                        f"{img.size}, expected {first_dims}."
                    )
                logging.warning(
                    "Skipping %s due to dimension mismatch: %s != %s",
                    filename,
                    img.size,
                    first_dims,
                )
                return None, None, first_dims

            rgb_img = img.convert("RGB")
            mask_img = img.convert("L")

            rgb_tensor = torch.from_numpy(np.array(rgb_img).astype(np.float32) / 255.0)
            mask_tensor = torch.from_numpy(np.array(mask_img).astype(np.float32) / 255.0)

            return rgb_tensor, mask_tensor, first_dims

    def load_from_zip(self, zip_file, heterogeneous_dimensions):
        """Loads images from the given zip file and returns batched tensors."""
        zip_path = os.path.join(folder_paths.get_input_directory(), zip_file)

        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"ZIP file not found: {zip_path}")

        images = []
        masks = []

        with zipfile.ZipFile(zip_path, "r") as archive:
            filenames = [
                f
                for f in archive.namelist()
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
                and not f.startswith("__MACOSX/")
                and not os.path.basename(f).startswith(".")
            ]

            filenames.sort()

            if not filenames:
                raise ValueError(f"No valid images found in the ZIP archive: {zip_file}")

            first_dimensions = None

            for filename in filenames:
                rgb_tensor, mask_tensor, first_dimensions = self._process_image_file(
                    archive, filename, first_dimensions, heterogeneous_dimensions
                )
                if rgb_tensor is not None and mask_tensor is not None:
                    images.append(rgb_tensor)
                    masks.append(mask_tensor)

        if not images:
            raise ValueError(f"No valid images could be processed from the ZIP archive: {zip_file}")

        batched_images = torch.stack(images)
        batched_masks = torch.stack(masks)

        return (batched_images, batched_masks, len(images))
