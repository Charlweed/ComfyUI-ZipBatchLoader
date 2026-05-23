"""
Registration point for the ComfyUI ZIP Batch Loader node.
"""

from .zip_batch_loader import ZipBatchLoader

NODE_CLASS_MAPPINGS = {"LoadImageBatchFromZip": ZipBatchLoader}

NODE_DISPLAY_NAME_MAPPINGS = {"LoadImageBatchFromZip": "Load Image Batch From Zip"}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
