"""
Unit tests for the ZipBatchLoader ComfyUI node.
"""

import os
import sys
import unittest
import zipfile
from unittest.mock import MagicMock

from PIL import Image

# Mock folder_paths before importing zip_batch_loader
sys.modules["folder_paths"] = MagicMock()

# Add parent dir to path to import zip_batch_loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import zip_batch_loader as zbl_module  # noqa: E402 # pylint: disable=wrong-import-position
from zip_batch_loader import ZipBatchLoader  # noqa: E402 # pylint: disable=wrong-import-position


class TestZipBatchLoader(unittest.TestCase):
    """Test suite for the ZipBatchLoader class."""

    test_dir: str
    zip_path: str
    hetero_zip_path: str
    mock_folder_paths: MagicMock

    def setUp(self):
        """Sets up the test environment by creating temporary zip files."""
        self.test_dir = os.path.dirname(__file__)
        self.zip_path = os.path.join(self.test_dir, "test.zip")
        self.hetero_zip_path = os.path.join(self.test_dir, "test_hetero.zip")

        # Mock the folder_paths module locally for the tested module
        self.mock_folder_paths = MagicMock()
        zbl_module.folder_paths = self.mock_folder_paths

        # Create test zip with uniform images
        with zipfile.ZipFile(self.zip_path, "w") as zf:
            for i in range(2):
                img = Image.new("RGB", (64, 64), color="red")
                with zf.open(f"img_{i}.png", "w") as f:
                    img.save(f, format="PNG")

        # Create test zip with heterogeneous images
        with zipfile.ZipFile(self.hetero_zip_path, "w") as zf:
            img1 = Image.new("RGB", (64, 64), color="red")
            with zf.open("img_0.png", "w") as f:
                img1.save(f, format="PNG")
            img2 = Image.new("RGB", (32, 32), color="blue")
            with zf.open("img_1.png", "w") as f:
                img2.save(f, format="PNG")

    def tearDown(self):
        """Cleans up the temporary zip files."""
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        if os.path.exists(self.hetero_zip_path):
            os.remove(self.hetero_zip_path)

    def test_input_types(self):
        """Tests that INPUT_TYPES returns the correct dictionary structure and files."""
        self.mock_folder_paths.get_input_directory.return_value = self.test_dir
        types = ZipBatchLoader.INPUT_TYPES()
        self.assertIn("required", types)
        self.assertIn("test.zip", types["required"]["zip_file"][0])
        self.assertIn("test_hetero.zip", types["required"]["zip_file"][0])

    def test_load_from_zip_uniform(self):
        """Tests loading a zip file with images of uniform dimensions."""
        self.mock_folder_paths.get_input_directory.return_value = self.test_dir
        loader = ZipBatchLoader()
        images, masks, count = loader.load_from_zip("test.zip", False)

        self.assertEqual(count, 2)
        self.assertEqual(images.shape, (2, 64, 64, 3))
        self.assertEqual(masks.shape, (2, 64, 64))

    def test_load_from_zip_hetero_false(self):
        """Tests ValueError is raised when heterogeneous_dimensions is False but dimensions vary."""
        self.mock_folder_paths.get_input_directory.return_value = self.test_dir
        loader = ZipBatchLoader()
        with self.assertRaises(ValueError):
            loader.load_from_zip("test_hetero.zip", False)

    def test_load_from_zip_hetero_true(self):
        """Tests that mismatched images are skipped when heterogeneous_dimensions is True."""
        self.mock_folder_paths.get_input_directory.return_value = self.test_dir
        loader = ZipBatchLoader()
        images, _masks, count = loader.load_from_zip("test_hetero.zip", True)

        # Should skip the second image
        self.assertEqual(count, 1)
        self.assertEqual(images.shape, (1, 64, 64, 3))


if __name__ == "__main__":
    unittest.main()
