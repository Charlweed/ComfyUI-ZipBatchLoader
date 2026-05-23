# Project Plan: ComfyUI ZIP Batch Loader Custom Node

## 1. Objective

Create a new, standalone Git repository for a ComfyUI custom node that implements the "Load Image Batch from Zip"
requirements. This ensures the node is modular, version-controlled, and easily installable via the ComfyUI Manager or
direct `git clone`.

## 2. Project Setup

### 2.1. Repository Details

- **Project Name**: `zip_batch_loader`
- **Location**: A directory independent of the main `charlweeds-geomancy` project workspace. For local development,
  `https://github.com/Charlweed/ComfyUI-ZipBatchLoader.git` has been created.
- **Primary Language**: Python 3.8+ (aligning with ComfyUI's standard interpreter requirements).

### 2.2. Directory Structure

```text
zip_batch_loader/
├── .gitignore
├── LICENSE              # MIT License recommended for ComfyUI nodes
├── README.md            # Installation instructions and examples
├── __init__.py          # Node registration
├── pyproject.toml       # minimal dependencies
├── requirements.txt     # minimal dependencies
├── tests                # unit and other tests
└── zip_batch_loader.py  # Core node logic
```

## 3. Implementation Phases

### Preparation:

Download a copy of the MIT LICENSE file into the project root.
Create an idiomatic README.md in the project root.
Create an idiomatic pyproject.toml file in the project root.

### Phase 1: Core Node Logic (`zip_batch_loader.py`)

- **Class Definition**: Implement the `ZipBatchLoader` class.
- **`INPUT_TYPES`**:
    - Query the ComfyUI `folder_paths.get_input_directory()` for `.zip` files to populate a dropdown widget.
- **`RETURN_TYPES`**: `("IMAGE", "MASK", "INT")`
- **`RETURN_NAMES`**: `("image", "mask", "count")`
- **`FUNCTION`**: `load_from_zip`
    - **Logic**:
        1. Resolve the absolute path to the selected `.zip` file.
        2. Open the archive using Python's built-in `zipfile` module.
        3. Iterate over `archive.namelist()`, filtering for `.png`, `.jpg`, `.jpeg`.
        4. Sort the filtered filenames alphabetically.
        5. Extract each image into memory, open it using `PIL.Image`.
        6. Convert each image to RGB (for the `IMAGE` output) and L/grayscale (for the `MASK` output).
        7. Convert the `PIL.Image` objects to normalized PyTorch tensors.
        8. Validate that all images have identical dimensions.
        9. Stack the tensors using `torch.stack()` or `torch.cat()` along the batch dimension.
        10. Return the batched `IMAGE` tensor, `MASK` tensor, and the total count.

### Phase 2: ComfyUI Registration (`__init__.py`)

- Import the `ZipBatchLoader` class from `zip_batch_loader.py`.
- Define the node mappings required by ComfyUI:
  ```python
  NODE_CLASS_MAPPINGS = {
      "LoadImageBatchFromZip": ZipBatchLoader
  }
  NODE_DISPLAY_NAME_MAPPINGS = {
      "LoadImageBatchFromZip": "Load Image Batch From Zip"
  }
  __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
  ```

### Phase 3: Testing & Validation

- **Unit tests**: Create and tun unit tests
- **Deployment**: Symlink or clone the repository into a local ComfyUI instance's `custom_nodes/` directory.
- **Basic Load**: Start ComfyUI and verify the node appears in the node browser without import errors.
- **Execution Test**:
    - Place a mock `geomancy_bundle_test.zip` in the ComfyUI `input` folder.
    - Create a test workflow with the new node.
    - Connect the node to a built-in `PreviewImage` or similar debug node (using a batch selector to extract specific
      frames).
    - Verify the output order exactly matches the alphabetical sort of the internal filenames.

### Phase 4: Release & Documentation

- Document the installation process in `README.md`.
- Detail the input/output tensor shapes and the strict dimension requirement.
- Commit all changes and push to a remote git repository (e.g., GitHub) to allow seamless installation.
