# Publishing to ComfyUI-Manager

This document outlines the procedures for adding this custom node to the public ComfyUI node ecosystem.

## Overview

The primary "clearinghouse" for ComfyUI custom nodes is the **ComfyUI-Manager** ecosystem. There are two main ways to list a node so it becomes searchable and installable via the Manager UI.

---

## Method 1: Comfy Registry (Recommended)

This is the modern, official centralized registry. It provides versioning and security scanning.

### Steps to Publish:

1.  **Register Publisher ID:**
    *   Create a publisher account at [registry.comfy.org](https://registry.comfy.org/).
    *   Set up a unique **Publisher ID**.

2.  **Generate API Key:**
    *   In your registry profile, create a "Registry Publishing API Key."

3.  **Initialize Metadata:**
    *   Install the Comfy CLI: `pip install comfy-cli`
    *   In the project root, run: `comfy node init`
    *   Update the generated `pyproject.toml` with your `PublisherId`, name, and version.

4.  **Publish:**
    *   Run: `comfy node publish`
    *   Provide your API key when prompted.

---

## Method 2: Manual Pull Request (Legacy)

This method involves manually adding the repository to the Manager's central list.

### Steps to Publish:

1.  **Fork the Manager Repository:**
    *   Fork [ltdrdata/ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager) on GitHub.

2.  **Edit `custom-node-list.json`:**
    *   Add an entry to the `custom_nodes` array:
        ```json
        {
          "author": "Charlweed",
          "title": "Load Image Batch From Zip",
          "reference": "https://github.com/Charlweed/ComfyUI-ZipBatchLoader",
          "category": "image",
          "description": "Loads a batch of images directly from a ZIP archive with alphabetical sorting."
        }
        ```

3.  **Submit Pull Request:**
    *   Commit the change to your fork and submit a PR to the `main` branch of the ComfyUI-Manager repository.

---

## Best Practices

*   **Requirements:** Ensure `requirements.txt` is always up to date.
*   **Versioning:** Use Semantic Versioning (e.g., `0.1.0`) in `pyproject.toml`.
*   **Testing:** Exhaustively test the node in a live ComfyUI instance before performing either of these steps.
