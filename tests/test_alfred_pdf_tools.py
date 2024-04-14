# pylint: disable=wrong-import-position, missing-class-docstring, unused-argument
"""Unit tests for alfred_pdf_tools"""
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

sys.path.append("./src")

from alfred_pdf_tools import (
    crop,
    decrypt,
    deskew,
    encrypt,
    extract_text,
    merge,
    optimize,
    scale,
    slice_,
    split_count,
    split_size,
)
from pypdf import PdfReader


class AlfredPdfToolsTests(unittest.TestCase):
    @patch("alfred_pdf_tools.wf.cache_data")
    @patch("workflow.notify.notify")
    def test_optimize(self, notify, cache_data) -> None:
        """Test optimize file action."""
        self.assertIsNone(optimize("-150", ["./resources/crazyones.pdf"]))
        self.assertIsNone(optimize("150", ['./resources/"crazyones".pdf']))
        self.assertIsNone(optimize("150", ["./resources/crazyones.pdf"]))
        self.assertIsNone(optimize("150", ["./resources/corrupted.pdf"]))

    @patch("alfred_pdf_tools.wf.cache_data")
    @patch("workflow.notify.notify")
    def test_deskew(self, notify, cache_data) -> None:
        """Test deskew file action."""
        self.assertIsNone(deskew(['./resources/"crazyones".pdf']))
        self.assertIsNone(deskew(["./resources/crazyones.pdf"]))
        self.assertIsNone(deskew(["./resources/corrupted.pdf"]))

    @patch("workflow.notify.notify")
    def test_encrypt(self, notify) -> None:
        """Test encrypt file action."""
        self.assertIsNone(encrypt("hunter2", ["./resources/encrypted.pdf"]))
        self.assertIsNone(encrypt("hunter2", ["./resources/crazyones.pdf"]))

    @patch("workflow.notify.notify")
    def test_decrypt(self, notify) -> None:
        """Test decrypt file action."""
        with self.assertRaises(SystemExit):
            decrypt("hunter2", ["./resources/encrypted.pdf"])
        self.assertIsNone(decrypt("test", ["./resources/encrypted.pdf"]))

    @patch("workflow.notify.notify")
    def test_merge(self, notify) -> None:
        """Test merge file action."""
        self.assertIsNone(
            merge("tmp_1", ["./resources/file_1.pdf", "./resources_mock/file_2.pdf"])
        )
        self.assertIsNone(
            merge("tmp_1", ["./resources/file_1.pdf", "./resources/file_2.pdf"])
        )
        reader = PdfReader("./resources/tmp_1.pdf")

        for n, page in enumerate(reader.pages, 1):
            self.assertEqual(int(page.extract_text()), n)

        self.assertIsNone(
            merge("", ["./resources/file_1.pdf", "./resources/file_2.pdf"])
        )
        reader = PdfReader("./resources/file_1 [merged].pdf")

        for n, page in enumerate(reader.pages, 1):
            self.assertEqual(int(page.extract_text()), n)

    @patch("workflow.notify.notify")
    def test_split_count(self, notify) -> None:
        """Test split by page count file action."""
        self.assertIsNone(
            split_count(
                "-4",
                "./resources/mult_pages_1.pdf",
                "part",
            )
        )
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

    @patch("workflow.notify.notify")
    def test_split_size(self, notify) -> None:
        """Test split by page count file action."""
        self.assertIsNone(
            split_size(
                "-0.05",
                "./resources/mult_pages_2.pdf",
                "part",
            )
        )
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

        self.assertIsNone(
            split_size(
                "0.3",
                "./resources/mult_pages_3.pdf",
                "part",
            )
        )
        size = Path("./resources/mult_pages_3 [part 1].pdf").stat().st_size
        self.assertLessEqual(size, 300000)
        reader = PdfReader("./resources/mult_pages_3 [part 1].pdf")
        size = Path("./resources/mult_pages_3 [part 2].pdf").stat().st_size
        self.assertLessEqual(size, 300000)
        reader = PdfReader("./resources/mult_pages_3 [part 2].pdf")
        size = Path("./resources/mult_pages_3 [part 3].pdf").stat().st_size
        self.assertLessEqual(size, 300000)
        reader = PdfReader("./resources/mult_pages_3 [part 3].pdf")

    @patch("workflow.notify.notify")
    def test_slice(self, notify) -> None:
        """Test slice file action."""
        self.assertIsNone(
            slice_(
                "0, 4-6, 9-",
                "./resources/mult_pages_4.pdf",
                True,
                "part",
            )
        )
        self.assertIsNone(
            slice_(
                "2, 6-4, 9-",
                "./resources/mult_pages_4.pdf",
                True,
                "part",
            )
        )
        self.assertIsNone(
            slice_(
                "2, 4-6, 9-",
                "./resources/mult_pages_4.pdf",
                True,
                "part",
            )
        )
        reader = PdfReader("./resources/mult_pages_4 [sliced].pdf")
        self.assertEqual(len(reader.pages), 6)
        pages = [2, 4, 5, 6, 9, 10]

        for i, page in enumerate(reader.pages):
            self.assertEqual(int(page.extract_text()), pages[i])

        self.assertIsNone(
            slice_(
                "2, 4-6, 9-",
                "./resources/mult_pages_4.pdf",
                False,
                "part",
            )
        )
        reader = PdfReader("./resources/mult_pages_4 [part 1].pdf")
        self.assertEqual(len(reader.pages), 1)
        pages = [2]

        for i, page in enumerate(reader.pages):
            self.assertEqual(int(page.extract_text()), pages[i])

        reader = PdfReader("./resources/mult_pages_4 [part 2].pdf")
        self.assertEqual(len(reader.pages), 3)
        pages = [4, 5, 6]

        for i, page in enumerate(reader.pages):
            self.assertEqual(int(page.extract_text()), pages[i])

        reader = PdfReader("./resources/mult_pages_4 [part 3].pdf")
        self.assertEqual(len(reader.pages), 2)
        pages = [9, 10]

        for i, page in enumerate(reader.pages):
            self.assertEqual(int(page.extract_text()), pages[i])

    def test_crop(self) -> None:
        """Test crop file action."""
        self.assertIsNone(crop(["./resources/landscape.pdf"]))
        reader = PdfReader("./resources/landscape [cropped].pdf")
        self.assertEqual(len(reader.pages), 4)

        for n, page in enumerate(reader.pages, 1):
            if n % 2 == 1:
                self.assertEqual(list(page.mediabox), [0.0, 0.0, 421, 595])
            else:
                self.assertEqual(list(page.mediabox), [421, 0.0, 842, 595])

        self.assertIsNone(crop(["./resources/portrait.pdf"]))
        reader = PdfReader("./resources/portrait [cropped].pdf")
        self.assertEqual(len(reader.pages), 4)

        for n, page in enumerate(reader.pages, 1):
            if n % 2 == 1:
                self.assertEqual(list(page.mediabox), [0.0, 0.0, 612, 396])
            else:
                self.assertEqual(list(page.mediabox), [0.0, 396, 612, 792])

    def test_scale(self) -> None:
        """Test scale file action."""
        sys.argv = [None, None, "8.3", "11.7"]
        self.assertIsNone(scale(["./resources/mult_pages_1.pdf"]))
        reader = PdfReader("./resources/mult_pages_1 [scaled].pdf")
        self.assertEqual(len(reader.pages), 10)

        for n, page in enumerate(reader.pages, 1):
            self.assertEqual(int(page.extract_text()), n)
            self.assertEqual(float(page.mediabox.width), 8.3 * 72)
            self.assertEqual(float(page.mediabox.height), 11.7 * 72)

    @patch("workflow.notify.notify")
    def test_extract_text(self, notify) -> None:
        """Test extract text file action."""
        with patch("builtins.print") as mock_print:
            extract_text(["./resources/mult_pages_1.pdf"])
            expected_calls = [
                call("1\n"),
                call("2\n"),
                call("3\n"),
                call("4\n"),
                call("5\n"),
                call("6\n"),
                call("7\n"),
                call("8\n"),
                call("9\n"),
                call("10\n"),
            ]
            mock_print.assert_has_calls(expected_calls)

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up resources."""
        Path("./resources/crazyones [optimized].pdf").unlink(missing_ok=True)
        Path("./resources/crazyones [deskewed].pdf").unlink(missing_ok=True)
        Path("./resources/crazyones [encrypted].pdf").unlink(missing_ok=True)
        Path("./resources/encrypted [decrypted].pdf").unlink(missing_ok=True)
        Path("./resources/tmp_1.pdf").unlink(missing_ok=True)
        Path("./resources/file_1 [merged].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_1 [part 1].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_1 [part 2].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_1 [part 3].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_2 [part 1].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_2 [part 2].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_2 [part 3].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_3 [part 1].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_3 [part 2].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_3 [part 3].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_4 [part 1].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_4 [part 2].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_4 [part 3].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_4 [sliced].pdf").unlink(missing_ok=True)
        Path("./resources/landscape [cropped].pdf").unlink(missing_ok=True)
        Path("./resources/portrait [cropped].pdf").unlink(missing_ok=True)
        Path("./resources/mult_pages_1 [scaled].pdf").unlink(missing_ok=True)
