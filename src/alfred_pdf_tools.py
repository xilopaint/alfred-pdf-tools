#!/usr/bin/env python3

"""
Usage:
    alfred_pdf_tools.py --optimize <res>
    alfred_pdf_tools.py --deskew
    alfred_pdf_tools.py --progress
    alfred_pdf_tools.py --encrypt <pwd>
    alfred_pdf_tools.py --decrypt <pwd>
    alfred_pdf_tools.py --mrg <filename>
    alfred_pdf_tools.py --mrg-trash <filename>
    alfred_pdf_tools.py --split-count <max_pages>
    alfred_pdf_tools.py --split-size <max_size>
    alfred_pdf_tools.py --slice-multi <query>
    alfred_pdf_tools.py --slice-single <query>
    alfred_pdf_tools.py --crop
    alfred_pdf_tools.py --scale <width> <height>

Optimize, encrypt and manipulate PDF files.

Options:
    --optimize <res>             Optimize PDF files.
    --deskew                     Deskew PDF files.
    --progress                   Track the enhancement progress.
    --encrypt <pwd>              Encrypt PDF files.
    --decrypt <pwd>              Decrypt PDF files.
    --mrg <filename>             Merge PDF files.
    --mrg-trash <filename>       Merge PDF files and move them to trash.
    --split-count <max_pages>    Split PDF file by page count.
    --split-size <max_size>      Split PDF file by file size.
    --slice-multi <query>        Multi-slice PDF files.
    --slice-single <query>       Single-slice PDF files.
    --crop                       Crop two-column pages.
    --scale <width> <height>     Scale PDF files to a given page size.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from copy import copy
from math import floor
from pathlib import Path

from docopt import docopt
from pypdf import PageObject, PageRange, PdfReader, PdfWriter, errors
from workflow import ICON_ERROR, Variables, Workflow, notify

UPDATE_SETTINGS = {"github_slug": "xilopaint/alfred-pdf-tools"}
HELP_URL = "https://github.com/xilopaint/alfred-pdf-tools"

wf = Workflow(update_settings=UPDATE_SETTINGS, help_url=HELP_URL)


class AlfredPdfToolsError(Exception):
    """Base class for the workflow exceptions."""


class DoubleQuotesPathError(AlfredPdfToolsError):
    """Raised when a PDF file has double quotes in its path."""


class SelectionError(AlfredPdfToolsError):
    """Raised when the user selects less than two PDF files."""


class MultiplePathsError(AlfredPdfToolsError):
    """Raised when the user selects PDF files from diferent dirnames."""


def handle_exceptions(func):
    """Decorator to handle exceptions in the wrapper function."""

    def wrapper(*args, **kwargs):  # pragma: no cover
        """Wrapper function."""
        try:
            func(*args, **kwargs)
        except ValueError:
            notify.notify("Alfred PDF Tools", "Invalid input.")
        except errors.PdfReadError:
            notify.notify("Alfred PDF Tools", "Encrypted files are not allowed.")
        except DoubleQuotesPathError:
            notify.notify(
                "Alfred PDF Tools",
                "This file action cannot handle a file path with double quotes.",
            )
        except SelectionError:
            notify.notify(
                "Alfred PDF Tools", "You must select at least two PDF files to merge."
            )
        except MultiplePathsError:
            notify.notify(
                "Alfred PDF Tools", "Cannot merge PDF files from different paths."
            )

    return wrapper


def run_k2pdfopt(cmd):
    """Execute k2pdfopt with the provided command caching the page numbers of the PDF
    file to track the progress of the process.

    Args:
        cmd (str): Command to run.

    Returns:
        int: Return code of the child process.
    """
    with subprocess.Popen(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        encoding="utf-8",
    ) as proc:
        for line in proc.stdout:
            if "Reading" in line:
                pg_cnt = line.split()[1]
                wf.cache_data("page_count", pg_cnt)

            if "SOURCE PAGE" in line:
                pg_num = line.split()[2]
                wf.cache_data("page_number", pg_num)

    wf.clear_cache(lambda cache_file: cache_file[:4] == "page")

    return proc.returncode


@handle_exceptions
def optimize(resolution, pdf_paths):
    """Optimize PDF files.

    Args:
        resolution (str): Resolution to be applied.
        pdf_paths (list): Paths to selected PDF files.
    """
    if int(resolution) < 0:
        raise ValueError  # pragma: no cover

    for pdf_path in pdf_paths:
        if '"' in pdf_path:
            raise DoubleQuotesPathError  # pragma: no cover

        cmd = f"'{Path(__file__).parent}/bin/k2pdfopt' {shlex.quote(pdf_path)} -ui- -as -mode copy -dpi {resolution} -o '%s [optimized].pdf' -x"
        returncode = run_k2pdfopt(cmd)

        if returncode == 0:
            notify.notify("Alfred PDF Tools", "Optimization successfully completed.")
        else:
            out_file = f"{Path(pdf_path).with_suffix('')} [optimized].pdf"
            Path(out_file).unlink(missing_ok=True)
            notify.notify("Alfred PDF Tools", "Optimization process failed.")


@handle_exceptions
def deskew(pdf_paths):
    """Deskew PDF files.

    Args:
        pdf_paths (list): Paths to selected PDF files.
    """
    for pdf_path in pdf_paths:
        if '"' in pdf_path:
            raise DoubleQuotesPathError  # pragma: no cover

        cmd = f"'{Path(__file__).parent}/bin/k2pdfopt' {shlex.quote(pdf_path)} -ui- -as -mode copy -n -o '%s [deskewed].pdf' -x"
        returncode = run_k2pdfopt(cmd)

        if returncode == 0:
            notify.notify("Alfred PDF Tools", "Deskew successfully completed.")
        else:
            notify.notify("Alfred PDF Tools", "Deskew process failed.")


def get_progress():  # pragma: no cover
    """Show enhancement progress."""
    wf.rerun = 1
    pg_num = wf.cached_data("page_number", max_age=0)
    pg_cnt = wf.cached_data("page_count", max_age=0)

    try:
        count = int(os.environ["count"])
    except KeyError:
        count = 0

    if not pg_cnt and not pg_num:
        title = "No enhancement action is running."
        wf.add_item(valid=True, title=title, icon=ICON_ERROR)

    if pg_cnt and not pg_num:
        title = "Reading the PDF file..."
        subtitle = progress_bar(count)
        wf.add_item(valid=True, title=title, subtitle=subtitle)

    if pg_cnt and pg_num:
        pct = str(int(round((float(pg_num) / float(pg_cnt)) * 100)))

        if pg_num != pg_cnt:
            title = f"Page {pg_num} of {pg_cnt} processed ({pct}% completed)"
            subtitle = progress_bar(count)
            wf.add_item(valid=True, title=title, subtitle=subtitle)
        else:
            wf.rerun = 0  # Stop re-running.
            title = f"Page {pg_cnt} of {pg_cnt} processed (100% completed)"
            wf.add_item(valid=True, title=title, icon="checkmark.png")

    count += 1

    wf.setvar("count", count)

    wf.send_feedback()


def progress_bar(count):  # pragma: no cover
    """Generate progress bar."""
    prog_bar = ["\u25CB"] * 5
    i = count % 5
    prog_bar[i] = "\u25CF"
    return "".join(prog_bar)


@handle_exceptions
def encrypt(pwd, pdf_paths):
    """Encrypt PDF files.

    Args:
        pwd (str): Password used in the encryption.
        pdf_paths (list): Paths to selected PDF files.
    """
    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(pwd)
        out_file = f"{Path(pdf_path).with_suffix('')} [encrypted].pdf"

        with open(out_file, "wb") as f:
            writer.write(f)

        notify.notify("Alfred PDF Tools", "Encryption successfully completed.")


@handle_exceptions
def decrypt(pwd, pdf_paths):
    """Decrypt PDF files.

    Args:
        pwd (str): Password used in the decryption.
        pdf_paths (list): Paths to selected PDF files.
    """
    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        reader.decrypt(pwd)

        writer = PdfWriter()

        try:
            for page in reader.pages:
                writer.add_page(page)
        except errors.PdfReadError:
            notify.notify("Alfred PDF Tools", "The entered password is not valid.")
            sys.exit(1)
        except errors.DependencyError:
            print(f"pip3 install pycryptodome -t '{Path(__file__).parent}'", end="")
            sys.exit(1)

        out_file = f"{Path(pdf_path).with_suffix('')} [decrypted].pdf"

        with open(out_file, "wb") as f:
            writer.write(f)

        notify.notify("Alfred PDF Tools", "Decryption successfully completed.")


@handle_exceptions
def merge(out_filename, pdf_paths):
    """Merge PDF files.

    Args:
        out_filename (str): Filename of the output PDF file without extension.
        pdf_paths (list): Paths to selected PDF files.
    """
    parent_paths = [Path(pdf_path).parent for pdf_path in pdf_paths]

    if len(pdf_paths) < 2:
        raise SelectionError  # pragma: no cover

    if not parent_paths[1:] == parent_paths[:-1]:
        raise MultiplePathsError  # pragma: no cover

    writer = PdfWriter()

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        writer.append(reader)

    writer.write(f"{parent_paths[0]}/{out_filename}.pdf")

    v = Variables(pdf_paths)
    print(json.dumps(v.obj))


@handle_exceptions
def split_count(max_pages, abs_path, suffix):
    """Split PDF file by page count.

    Args:
        max_pages (str): Maximum amount of pages for each output PDF file.
        abs_path (str): Absolute path of the input PDF file.
        suffix (str): Suffix for the output filenames.
    """
    if int(max_pages) < 0:
        raise ValueError  # pragma: no cover

    reader = PdfReader(abs_path)

    pg_cnt = int(max_pages)
    num_pages = len(reader.pages)
    page_ranges = [PageRange(slice(n, n + pg_cnt)) for n in range(0, num_pages, pg_cnt)]

    for n, page_range in enumerate(page_ranges, 1):
        writer = PdfWriter()
        writer.append(reader, pages=page_range)
        writer.write(f"{Path(abs_path).with_suffix('')} [{suffix} {n}].pdf")


@handle_exceptions
def split_size(max_size, abs_path, suffix):
    """Split PDF file by file size.

    Args:
        max_size (str): Maximum file size for each output PDF file.
        abs_path (str): Absolute path of the input PDF file.
        suffix (str): Suffix for the output filenames.
    """
    if float(max_size) < 0:
        raise ValueError  # pragma: no cover

    max_chunk_sz = float(max_size) * 1000000
    reader = PdfReader(abs_path)
    pg_cnt = len(reader.pages)
    pg_sizes = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        for n, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)

            with open(f"{tmp_dir}/page{n}", "wb") as f:
                writer.write(f)

            tmp_file_size = os.path.getsize(f"{tmp_dir}/page{n}")
            pg_sizes.append(tmp_file_size)

    inp_file_size = os.path.getsize(abs_path)
    sum_pg_sizes = sum(pg_sizes)
    dividend = min(inp_file_size, sum_pg_sizes)
    divisor = max(inp_file_size, sum_pg_sizes)
    quotient = dividend / divisor

    start = 0
    stop = 1
    pg_num = 0

    if quotient > 0.95:  # pylint: disable=too-many-nested-blocks
        pg_chunks = [[(0, pg_sizes.pop(0))]]

        for n, pg_size in enumerate(pg_sizes, 1):
            if sum(ps for _, ps in pg_chunks[-1]) + pg_size < max_chunk_sz:
                pg_chunks[-1].append((n, pg_size))
            else:
                pg_chunks.append([(n, pg_size)])

        slices = [PageRange(slice(n[0][0], n[-1][0] + 1)) for n in pg_chunks]

        for n, slice__ in enumerate(slices, 1):
            writer = PdfWriter()
            writer.append(reader, pages=slice__)
            writer.write(f"{Path(abs_path).with_suffix('')} [{suffix} {n}].pdf")
    else:
        while not stop > pg_cnt:
            out_file_name = (
                f"{Path(abs_path).with_suffix('')} [{suffix} {pg_num + 1}].pdf"
            )
            chunk = pg_sizes[start:stop]
            chunk_size = sum(chunk)
            chunk_pg_cnt = len(chunk)

            if chunk_size < max_chunk_sz:
                if stop != pg_cnt:
                    stop += 1
                else:
                    writer = PdfWriter()
                    writer.append(reader, pages=(start, stop))
                    writer.write(out_file_name)
                    break
            else:
                if chunk_pg_cnt == 1:
                    writer = PdfWriter()
                    writer.append(reader, pages=(start, stop))
                    writer.write(out_file_name)
                    start = stop
                    stop += 1
                    pg_num += 1
                else:
                    stop -= 1
                    writer = PdfWriter()
                    writer.append(reader, pages=(start, stop))
                    writer.write(out_file_name)
                    chunk_size = os.path.getsize(out_file_name)
                    next_page = pg_sizes[stop : stop + 1][0]

                    if chunk_size + next_page < max_chunk_sz:
                        os.remove(out_file_name)
                        chunk_size_real = chunk_size / (stop - start)

                        pg_sizes_real = []

                        for i in range(pg_cnt):
                            if start <= i < stop:
                                pg_sizes_real.append(chunk_size_real)
                            else:
                                pg_sizes_real.append(pg_sizes[i])

                        pg_sizes = pg_sizes_real
                        stop += 1
                    else:
                        start = stop
                        stop += 1
                        pg_num += 1


@handle_exceptions
def slice_(query, abs_path, is_single, suffix):
    """Slice PDF files.

    Args:
        query (str): Syntax indicating page numbers and/or page ranges (e.g. "2, 4-6, 9-")
        abs_path (str): Absolute path of the input PDF file.
        is_single (bool): `True` for a single output file.
        suffix (str): Suffix for the output filenames.
    """
    # Query parameter validation.
    if re.search(r"^\D|^0.|\D0\D|\D0$", query):
        raise ValueError  # pragma: no cover

    pg_ranges = [x.split("-") for x in query.split(",")]

    for pg_range in pg_ranges:
        if len(pg_range) > 1 and pg_range[1] != "":
            if int(pg_range[0]) > int(pg_range[1]):
                raise ValueError  # pragma: no cover

    reader = PdfReader(abs_path)
    pg_cnt = len(reader.pages)

    slices = [
        (int(x[0]) - 1, int(x[1] or pg_cnt))
        if len(x) > 1
        else (int(x[0]) - 1, int(x[0]))
        for x in pg_ranges
    ]

    if is_single:
        writer = PdfWriter()

        for slice__ in slices:
            writer.append(reader, pages=slice__)
        writer.write(f"{Path(abs_path).with_suffix('')} [sliced].pdf")
    else:
        for part_num, slice__ in enumerate(slices, 1):
            writer = PdfWriter()
            writer.append(reader, pages=slice__)
            writer.write(f"{Path(abs_path).with_suffix('')} [{suffix} {part_num}].pdf")


@handle_exceptions
def crop(pdf_paths):
    """Crop two-column pages.

    Args:
        pdf_paths (list): Paths to selected PDF files.
    """
    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            # Make two copies of the input page.
            page_copy_1 = copy(page)
            page_copy_2 = copy(page)

            # The new mediaboxes are the previous cropboxes.
            page_copy_1.mediabox = copy(page_copy_1.cropbox)
            page_copy_2.mediabox = copy(page_copy_1.cropbox)

            x1, y1 = page_copy_1.mediabox.lower_left
            x2, y2 = page_copy_1.mediabox.upper_right

            x1, y1 = floor(x1), floor(y1)
            x2, y2 = floor(x2), floor(y2)
            x3, y3 = x1 + floor((x2 - x1) / 2), y1 + floor((y2 - y1) / 2)

            if (x2 - x1) > (y2 - y1):
                # Horizontal
                page_copy_1.mediabox.lower_left = (x1, y1)
                page_copy_1.mediabox.upper_right = (x3, y2)

                page_copy_2.mediabox.lower_left = (x3, y1)
                page_copy_2.mediabox.upper_right = (x2, y2)
            else:
                # Vertical
                page_copy_1.mediabox.lower_left = (x1, y1)
                page_copy_1.mediabox.upper_right = (x2, y3)

                page_copy_2.mediabox.lower_left = (x1, y3)
                page_copy_2.mediabox.upper_right = (x2, y2)

            page_copy_1.artbox = page_copy_1.mediabox
            page_copy_1.bleedbox = page_copy_1.mediabox
            page_copy_1.cropbox = page_copy_1.mediabox

            page_copy_2.artbox = page_copy_2.mediabox
            page_copy_2.bleedbox = page_copy_2.mediabox
            page_copy_2.cropbox = page_copy_2.mediabox

            writer.add_page(page_copy_1)
            writer.add_page(page_copy_2)

        out_file = f"{Path(pdf_path).with_suffix('')} [cropped].pdf"

        with open(out_file, "wb") as f:
            writer.write(f)


@handle_exceptions
def scale(pdf_paths):
    """Scale PDF files to a given page size.

    Args:
        pdf_paths (list): Paths to selected PDF files.
    """
    width = float(sys.argv[2]) * 72
    height = float(sys.argv[3]) * 72

    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            out_page = PageObject.create_blank_page(None, width, height)
            out_page.merge_page(page)

            writer.add_page(out_page)

        out_file = f"{Path(pdf_path).with_suffix('')} [scaled].pdf"

        with open(out_file, "wb") as f:
            writer.write(f)


def main(wf):  # pylint: disable=redefined-outer-name  # pragma: no cover
    """Run workflow."""
    args = docopt(__doc__)
    query = wf.args[1] if len(wf.args) > 1 else None
    abs_path = os.environ["abs_path"]
    pdf_paths = abs_path.split("\t")
    suffix = os.environ["suffix"]

    if args["--optimize"]:
        optimize(query, pdf_paths)
    elif args["--deskew"]:
        deskew(pdf_paths)
    elif args["--progress"]:
        get_progress()
    elif args["--encrypt"]:
        encrypt(query, pdf_paths)
    elif args["--decrypt"] is not None:
        decrypt(query, pdf_paths)
    elif args["--mrg"]:
        merge(query, pdf_paths)
    elif args["--mrg-trash"]:
        merge(query, pdf_paths)
    elif args["--split-count"]:
        split_count(query, abs_path, suffix)
    elif args["--split-size"]:
        split_size(query, abs_path, suffix)
    elif args["--slice-multi"]:
        slice_(query, abs_path, False, suffix)
    elif args["--slice-single"]:
        slice_(query, abs_path, True, suffix)
    elif args["--crop"]:
        crop(pdf_paths)
    elif args["--scale"]:
        scale(pdf_paths)

    if wf.update_available:
        notify.notify(
            "Alfred PDF Tools", "A newer version of the workflow is available.", "Glass"
        )
        wf.start_update()


if __name__ == "__main__":
    sys.exit(wf.run(main))  # pragma: no cover
