# Requirements: ComfyUI "Load Image Batch from Zip" Node

## 1. Overview

A custom ComfyUI node designed to read a ZIP archive containing multiple images, sort them predictably, and output them
as batched `IMAGE` and `MASK` tensors. This node is critical for the Charlweed's Geomancy pipeline to ingest a single
bundled artifact containing the blueprint and semantic class masks. The "Charlweed's Geomancy" project is local at
`file:../../../hymerfania/charlweeds-geomancy`, but this project does not have any dependencies on that project. The
local ComfyUI project is at `file:../../ComfyUI`

## 2. Core Functionality

- **Archive Extraction**: Read `.zip` files directly in-memory without requiring manual extraction by the user on the
  filesystem.
- **Image Decoding**: Decode standard image formats (PNG, JPG) found within the archive.
- **Sorting**: Guarantee a predictable order of images. Alphabetical sorting by filename is required to respect the
  `000_`, `010_` prefix convention used in the Geomancy bundles.
- **Batching**: Stack the loaded images into standard ComfyUI 4D tensor formats (`[B, H, W, C]` for images).

## 3. Node Specifications

### 3.1. Inputs

- `zip_file` (STRING): The file path to the target ZIP archive. This should ideally utilize ComfyUI's standard
  file-picker UI, populating a dropdown with `.zip` files located in the ComfyUI `input` directory (or a dedicated
  `input/zips` subdirectory).
- `heterogeneous_dimensions` (BOOLEAN): If true, the node does not enforce that all images and masks are the same size.
  The default value is FALSE.

### 3.2. Outputs

- `IMAGE` (TENSOR): A batched tensor of the RGB data for all images in the ZIP. Shape: `[B, H, W, 3]`.
- `MASK` (TENSOR): A batched tensor of the Mask (alpha or grayscale) data. Shape: `[B, H, W]`.
- `COUNT` (INT, Optional): The total number of images successfully loaded in the batch.

## 4. Constraints & Edge Cases

- **Uniform Dimensions**: If heterogeneous_dimensions is false (the default), the node enforces that all images in the
  ZIP have the exact same dimensions (`H x W`) to successfully batch them into a single tensor. If
  heterogeneous_dimensions is false and dimensions mismatch, the node MUST throw a descriptive error rather than
  silently failing or cropping, as dimension mismatches indicate a broken Geomancy bundle. However, if
  `heterogeneous_dimensions` is true, images that are not the same size asa the first image are skipped, and a warning
  is logged.
- **Non-Image Files**: The node must safely ignore non-image files (e.g., `manifest.json`, `.txt`) present in the ZIP
  archive.
- **Empty Archives**: Throw a clear error if the ZIP contains no valid images.

## 5. Integration Context

This node directly replaces the hallucinated capability of `ComfyUI-TinyBee`. It will serve as the root input node in
the `geomancy_battlemap_sd15_v3_gui.json` workflow, receiving the `geomancy_bundle_{timestamp}.zip` and feeding the
batched output to downstream node(s) that will unbatch or select specific indices for the `000_blueprint` and `010_`
through `050_` masks.
