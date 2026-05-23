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


# noinspection PyPep8Naming
class ZipBatchLoader:
    """
    A custom ComfyUI node that loads a batch of images and masks from a ZIP archive.

    This node reads a ZIP file from the ComfyUI input directory, extracts image files,
    sorts them alphabetically, and stacks them into batched tensors. It is designed
    to handle standardized datasets (like Geomancy bundles) efficiently in-memory.

    Attributes:
        RETURN_TYPES (tuple): The types of data returned by the node (IMAGE, MASK, INT).
        RETURN_NAMES (tuple): The names of the returned outputs (image, mask, count).
        FUNCTION (str): The name of the entry point method (load_from_zip).
        CATEGORY (str): The category under which the node appears in ComfyUI.
    """

    @classmethod
    def INPUT_TYPES(cls):  # pylint: disable=invalid-name
        """
        Defines the input parameters for the node.

        Queries the ComfyUI input directory for available ZIP files to populate
        the dropdown menu.

        Returns:
            dict: A dictionary defining the required and optional inputs.
                - zip_file: A dropdown list of .zip files in the input folder.
                - heterogeneous_dimensions: A boolean toggle. If True, allows images
                  of different sizes to be skipped instead of raising an error.
        """
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
        """
        Extracts and processes a single image file from the ZIP archive.

        This helper method reads the image data into memory, validates its dimensions
        against the first image in the batch, and converts it into PyTorch tensors.

        Args:
            archive (zipfile.ZipFile): The open ZIP archive object.
            filename (str): The internal path/name of the file to process.
            first_dims (tuple, optional): The (width, height) of the first image
                processed in this batch. Used for dimension validation.
            heterogeneous_dims (bool): If True, skips images with mismatched dimensions.

        Returns:
            tuple: A tuple containing:
                - rgb_tensor (torch.Tensor or None): Normalized RGB image tensor [H, W, 3].
                - mask_tensor (torch.Tensor or None): Normalized mask tensor [H, W].
                - first_dims (tuple): The updated or original reference dimensions.

        Raises:
            ValueError: If heterogeneous_dims is False and a dimension mismatch is found.
        """
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

    def load_from_zip(self, zip_file: str, heterogeneous_dimensions: bool):
        """
        The main entry point for the node. Loads and batches images from the ZIP.

        Args:
            zip_file (str): The filename of the ZIP archive located in the
                ComfyUI input directory.
            heterogeneous_dimensions (bool): If True, the node will skip images
                that do not match the dimensions of the first valid image found
                in the archive. If False, any mismatch will raise a ValueError.

        Returns:
            tuple: A tuple containing:
                - IMAGE (torch.Tensor): A batched tensor of shape [B, H, W, 3].
                - MASK (torch.Tensor): A batched tensor of shape [B, H, W].
                - COUNT (int): The number of images successfully loaded.

        Raises:
            FileNotFoundError: If the specified ZIP file does not exist.
            ValueError: If no valid images are found or if processing fails due
                to dimension mismatches (when heterogeneous_dimensions is False).
        """
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

        return batched_images, batched_masks, len(images)
