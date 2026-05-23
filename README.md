# ComfyUI ZIP Batch Loader

[![Comfy Registry](https://img.shields.io/badge/Comfy%20Registry-ZipBatchLoader-blue)](https://registry.comfy.org/publishers/charlweed/nodes/zipbatchloader)

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

### Via Comfy CLI (Recommended)

If you have the [Comfy CLI](https://github.com/comfyanonymous/comfy-cli) installed, you can install this node by running:

```bash
comfy node install comfyui-zip-batch-loader
```

### Via ComfyUI Manager

1. Open the **Manager** in ComfyUI.
2. Click on **Custom Nodes Manager**.
3. Search for `ZipBatchLoader` or `comfyui-zip-batch-loader`.
4. Click **Install**.

### Manual Installation

1. Navigate to your ComfyUI `custom_nodes` directory.
2. Clone this repository:
   ```bash
   git clone https://github.com/Charlweed/ComfyUI-ZipBatchLoader.git zip_batch_loader
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
