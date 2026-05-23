# ComfyUI ZIP Batch Loader

A custom ComfyUI node that loads a batch of images directly from a ZIP archive. This node reads the archive in-memory,
sorts the images alphabetically by filename, and outputs them as batched `IMAGE` and `MASK` tensors, maintaining a
predictable order.

## Features

- **Direct ZIP Loading:** Reads `.zip` files from the ComfyUI `input` directory without manual extraction.
- **Alphabetical Sorting:** Ensures images are loaded in a predictable order based on filenames (e.g., `000_image.png`,
  `010_image.png`).
- **Batched Outputs:** Outputs standard ComfyUI 4D tensors for both RGB images and Grayscale masks.
- **Dimension Validation:** Configurable behavior for handling images of varying sizes within the same archive.

## Installation

### Manual Installation

1. Navigate to your ComfyUI `custom_nodes` directory.
2. Clone this repository:
   ```bash
   git clone <repository_url> zip_batch_loader
   ```
3. Restart ComfyUI.

## Usage

The node will appear in the ComfyUI node browser under **Load Image Batch From Zip**.
Place your `.zip` archives into the ComfyUI `input` directory.

### Inputs

- `zip_file`: Select a `.zip` file from the ComfyUI input directory.
- `heterogeneous_dimensions` (Default: `False`):
    - If `False`, all images in the ZIP must have the exact same dimensions. An error is thrown if a mismatch occurs.
    - If `True`, images that do not match the dimensions of the first image in the archive will be skipped, and a
      warning will be logged.

### Outputs

- `IMAGE`: Batched tensor of RGB data `[B, H, W, 3]`.
- `MASK`: Batched tensor of Mask/Grayscale data `[B, H, W]`.
- `COUNT`: The total number of images successfully loaded in the batch.
