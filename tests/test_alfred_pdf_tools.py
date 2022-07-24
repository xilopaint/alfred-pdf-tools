# pylint: disable=wrong-import-position, missing-class-docstring
"""Unit tests for alfred_pdf_tools"""
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.append("./src")

from PyPDF2 import PdfReader

from alfred_pdf_tools import (
    optimize,
    deskew,
    encrypt,
    decrypt,
    merge,
    split_count,
    split_size,
    slice_,
    crop,
    scale,
)


class AlfredPdfToolsTests(unittest.TestCase):
    @patch("alfred_pdf_tools.wf.cache_data")
    @patch("workflow.notify.notify")
    def test_optimize(self, notify, cache_data):
        """Test optimize file action."""
        self.assertIsNone(optimize("150", ["./resources/crazyones.pdf"]))
        cache_data.assert_called()
        notify.assert_called_once_with(
            "Alfred PDF Tools", "Optimization successfully completed."
        )

        self.assertIsNone(optimize("150", ["./resources/corrupted.pdf"]))

    @patch("alfred_pdf_tools.wf.cache_data")
    @patch("workflow.notify.notify")
    def test_deskew(self, notify, cache_data):
        """Test deskew file action."""
        self.assertIsNone(deskew(["./resources/crazyones.pdf"]))
        cache_data.assert_called()
        notify.assert_called_once_with(
            "Alfred PDF Tools", "Deskew successfully completed."
        )

        self.assertIsNone(deskew(["./resources/corrupted.pdf"]))

    @patch("workflow.notify.notify")
    def test_encrypt(self, notify):
        """Test encrypt file action."""
        self.assertIsNone(encrypt("hunter2", ["./resources/crazyones.pdf"]))
        notify.assert_called_once_with(
            "Alfred PDF Tools", "Encryption successfully completed."
        )

    @patch("workflow.notify.notify")
    def test_decrypt(self, notify):
        """Test decrypt file action."""
        self.assertIsNone(decrypt("test", ["./resources/encrypted_file.pdf"]))
        notify.assert_called_once_with(
            "Alfred PDF Tools", "Decryption successfully completed."
        )

        with self.assertRaises(SystemExit):
            decrypt("hunter2", ["./resources/encrypted_file.pdf"])

    def test_merge(self):
        """Test merge file action."""
        self.assertIsNone(
            merge("tmp_1", ["./resources/file_1.pdf", "./resources/file_2.pdf"])
        )
        reader = PdfReader("./resources/tmp_1.pdf")

        for n, page in enumerate(reader.pages, 1):
            self.assertEqual(int(page.extract_text()), n)

        shutil.copy("./resources/file_1.pdf", "./resources/file_3.pdf")
        shutil.copy("./resources/file_2.pdf", "./resources/file_4.pdf")

        self.assertIsNone(
            merge("tmp_2", ["./resources/file_3.pdf", "./resources/file_4.pdf"])
        )
        reader = PdfReader("./resources/tmp_2.pdf")

        for n, page in enumerate(reader.pages, 1):
            self.assertEqual(int(page.extract_text()), n)

    def test_split_count(self):
        """Test split by page count file action."""
        self.assertIsNone(
            split_count(
                "4",
                "./resources/mult_pages_1.pdf",
                "part",
            )
        )
        reader = PdfReader("./resources/mult_pages_1 [part 1].pdf")
        self.assertEqual(len(reader.pages), 4)

        for n, page in enumerate(reader.pages, 1):
            self.assertEqual(int(page.extract_text()), n)

        reader = PdfReader("./resources/mult_pages_1 [part 2].pdf")
        self.assertEqual(len(reader.pages), 4)

        for n, page in enumerate(reader.pages, 5):
            self.assertEqual(int(page.extract_text()), n)

        reader = PdfReader("./resources/mult_pages_1 [part 3].pdf")
        self.assertEqual(len(reader.pages), 2)

        for n, page in enumerate(reader.pages, 9):
            self.assertEqual(int(page.extract_text()), n)

    def test_split_size(self):
        """Test split by page count file action."""
        self.assertIsNone(
            split_size(
                "0.05",
                "./resources/mult_pages_2.pdf",
                "part",
            )
        )
        size = Path("./resources/mult_pages_2 [part 1].pdf").stat().st_size
        self.assertLessEqual(size, 50000)
        reader = PdfReader("./resources/mult_pages_2 [part 1].pdf")
        self.assertEqual(len(reader.pages), 4)

        for n, page in enumerate(reader.pages, 1):
            self.assertEqual(int(page.extract_text()), n)

        size = Path("./resources/mult_pages_2 [part 2].pdf").stat().st_size
        self.assertLessEqual(size, 50000)
        reader = PdfReader("./resources/mult_pages_2 [part 2].pdf")
        self.assertEqual(len(reader.pages), 4)

        for n, page in enumerate(reader.pages, 5):
            self.assertEqual(int(page.extract_text()), n)

        size = Path("./resources/mult_pages_2 [part 3].pdf").stat().st_size
        self.assertLessEqual(size, 50000)
        reader = PdfReader("./resources/mult_pages_2 [part 3].pdf")
        self.assertEqual(len(reader.pages), 2)

        for n, page in enumerate(reader.pages, 9):
            self.assertEqual(int(page.extract_text()), n)

    def test_slice(self):
        """Test slice file action."""
        self.assertIsNone(
            slice_(
                "2, 4-6, 9-",
                "./resources/mult_pages_3.pdf",
                True,
                "part",
            )
        )
        reader = PdfReader("./resources/mult_pages_3 [sliced].pdf")
        self.assertEqual(len(reader.pages), 6)
        pages = [2, 4, 5, 6, 9, 10]
        for i, page in enumerate(reader.pages):
            self.assertEqual(int(page.extract_text()), pages[i])

        self.assertIsNone(
            slice_(
                "2, 4-6, 9-",
                "./resources/mult_pages_3.pdf",
                False,
                "part",
            )
        )
        reader = PdfReader("./resources/mult_pages_3 [part 1].pdf")
        self.assertEqual(len(reader.pages), 1)
        pages = [2]

        for i, page in enumerate(reader.pages):
            self.assertEqual(int(page.extract_text()), pages[i])

        reader = PdfReader("./resources/mult_pages_3 [part 2].pdf")
        self.assertEqual(len(reader.pages), 3)
        pages = [4, 5, 6]

        for i, page in enumerate(reader.pages):
            self.assertEqual(int(page.extract_text()), pages[i])

        reader = PdfReader("./resources/mult_pages_3 [part 3].pdf")
        self.assertEqual(len(reader.pages), 2)
        pages = [9, 10]

        for i, page in enumerate(reader.pages):
            self.assertEqual(int(page.extract_text()), pages[i])

    def test_crop(self):
        """Test crop file action."""
        self.assertIsNone(crop(["./resources/landscape.pdf"]))

    def test_scale(self):
        """Test scale file action."""
        sys.argv = [None, None, "8.3", "11.7"]
        self.assertIsNone(scale(["./resources/mult_pages_1.pdf"]))
        reader = PdfReader("./resources/mult_pages_1 [scaled].pdf")
        self.assertEqual(len(reader.pages), 10)

        for n, page in enumerate(reader.pages, 1):
            self.assertEqual(int(page.extract_text()), n)
            self.assertEqual(float(page.mediabox.width), 8.3 * 72)
            self.assertEqual(float(page.mediabox.height), 11.7 * 72)

    @classmethod
    def tearDownClass(cls):
        """Clean up resources."""
        Path("./resources/crazyones [optimized].pdf").unlink(missing_ok=True)
        Path("./resources/crazyones [deskewed].pdf").unlink(missing_ok=True)
        Path("./resources/crazyones [encrypted].pdf").unlink(missing_ok=True)
        Path("./resources/encrypted_file [decrypted].pdf").unlink(missing_ok=True)
        Path("./resources/tmp_1.pdf").unlink(missing_ok=True)
        Path("./resources/tmp_2.pdf").unlink(missing_ok=True)
        Path("./resources/file_3.pdf").unlink(missing_ok=True)
        Path("./resources/file_4.pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_1 [part 1].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_1 [part 2].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_1 [part 3].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_2 [part 1].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_2 [part 2].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_2 [part 3].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_3 [sliced].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_3 [part 1].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_3 [part 2].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_3 [part 3].pdf").unlink(missing_ok=True)
        Path("./resources/landscape [cropped].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_1 [scaled].pdf").unlink(missing_ok=True)
