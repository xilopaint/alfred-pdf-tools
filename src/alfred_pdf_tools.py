#!/usr/bin/python3

"""
Usage:
    alfred_pdf_tools.py --optimize <query>
    alfred_pdf_tools.py --deskew <query>
    alfred_pdf_tools.py --progress <query>
    alfred_pdf_tools.py --encrypt <query>
    alfred_pdf_tools.py --decrypt <query>
    alfred_pdf_tools.py --mrg <query>
    alfred_pdf_tools.py --mrg-trash <query>
    alfred_pdf_tools.py --split-count <query>
    alfred_pdf_tools.py --split-size <query>
    alfred_pdf_tools.py --slice-multi <query>
    alfred_pdf_tools.py --slice-single <query>
    alfred_pdf_tools.py --crop <query>
    alfred_pdf_tools.py --scale <query>

Optimize, encrypt and manipulate PDF files.

Options:
    [--optimize <query>]    Optimize PDF files.
    --deskew                Deskew PDF files.
    --progress              Track the enhancement progress.
    --encrypt <query>       Encrypt PDF files.
    --decrypt <query>       Decrypt PDF files.
    --mrg <query>           Merge PDF files.
    --mrg-trash <query>     Merge PDF files and move them to trash.
    --split-count <query>   Split PDF file by page count.
    --split-size <query>    Split PDF file by file size.
    --slice-multi <query>   Multi-slice PDF files.
    --slice-single <query>  Single-slice PDF files.
    --crop                  Crop two-column pages.
    --scale <query>         Scale PDF files to a given page size.
"""

import os
import sys
import tempfile
from pathlib import Path
from subprocess import Popen, PIPE

from docopt import docopt
from pikepdf import Pdf, Encryption, PasswordError
from send2trash import send2trash

from workflow import Workflow, notify, ICON_ERROR


UPDATE_SETTINGS = {'github_slug': 'xilopaint/alfred-pdf-tools'}
HELP_URL = 'https://github.com/xilopaint/alfred-pdf-tools'


class AlfredPdfToolsError(Exception):
    """The base class for the workflow exceptions."""
    pass


class NotIntegerError(AlfredPdfToolsError):
    """Raised when the user input is not an integer."""
    pass


class NegativeValueError(AlfredPdfToolsError):
    """Raised when the user input is a negative integer."""
    pass


class SelectionError(AlfredPdfToolsError):
    """Raised when the user selects less than two PDF files."""
    pass


class MultiplePathsError(AlfredPdfToolsError):
    """Raised when the user selects PDF files from diferent dirnames."""
    pass


class SyntaxError(AlfredPdfToolsError):
    """Raised when the input is not a valid syntax."""
    pass


class IndexError(AlfredPdfToolsError):
    """Raised when the inputted page number is out of range."""
    pass


class StartValueZeroError(AlfredPdfToolsError):
    """Raise when the inputted page number is zero."""
    pass


class StartValueReverseError(AlfredPdfToolsError):
    """Raised when a page range is set in reverse order."""
    pass


def optimize(resolution, pdf_paths):
    """Optimize PDF files.

    Args:
        resolution (str): Resolution to be applied.
        pdf_paths (list): Paths to selected PDF files.
    """
    try:
        if resolution:
            if not resolution.lstrip('+-').isdigit():
                raise NotIntegerError

        if resolution:
            if int(resolution) < 0:
                raise NegativeValueError

        if not resolution:
            resolution = 150

        for pdf_path in pdf_paths:
            cmd = f'echo -y | {os.path.dirname(__file__)}/bin/k2pdfopt "{pdf_path}" -as -mode copy -dpi {resolution} -o "%s (optimized).pdf" -x'  # noqa
            proc = Popen(cmd, shell=True, stdout=PIPE)

            while proc.poll() is None:  # Loop while the subprocess is running.
                line = proc.stdout.readline().decode('utf-8')

                if 'Reading' in line:
                    pg_cnt = line.split()[1]
                    wf.cache_data('page_count', pg_cnt)

                if 'SOURCE PAGE' in line:
                    pg_num = line.split()[2]
                    wf.cache_data('page_number', pg_num)

            notify.notify(
                'Alfred PDF Tools',
                'Optimization successfully completed.'
            )
    except NotIntegerError:
        notify.notify(
            'Alfred PDF Tools',
            'The argument is not an integer.'
        )
    except NegativeValueError:
        notify.notify(
            'Alfred PDF Tools',
            'Negative integer is not a valid argument.'
        )


def deskew(pdf_paths):
    """Deskew PDF files.

    Args:
        pdf_paths (list): Paths to selected PDF files.
    """
    for pdf_path in pdf_paths:
        cmd = f'echo -y | {os.path.dirname(__file__)}/bin/k2pdfopt "{pdf_path}" -as -mode copy -n -o "%s [deskewed].pdf" -x'  # noqa
        proc = Popen(cmd, shell=True, stdout=PIPE)

        while proc.poll() is None:  # Loop while the subprocess is running.
            line = proc.stdout.readline().decode('utf-8')

            if 'Reading' in line:
                pg_cnt = line.split()[1]
                wf.cache_data('page_count', pg_cnt)

            if 'SOURCE PAGE' in line:
                pg_num = line.split()[2]
                wf.cache_data('page_number', pg_num)

        notify.notify(
            'Alfred PDF Tools',
            'Deskew successfully completed.'
        )


def get_progress():
    """Show enhancement progress."""
    wf.rerun = 1
    pg_num = wf.cached_data('page_number', max_age=0)
    pg_cnt = wf.cached_data('page_count', max_age=0)

    try:
        count = int(os.environ['count'])
    except KeyError:
        count = 0

    if not pg_cnt and not pg_num:
        title = 'No enhancement action is running.'
        wf.add_item(valid=True, title=title, icon=ICON_ERROR)

    if pg_cnt and not pg_num:
        title = 'Reading the PDF file...'
        subtitle = progress_bar(count)
        wf.add_item(valid=True, title=title, subtitle=subtitle)

    if pg_cnt and pg_num:
        pct = str(int(round((float(pg_num) / float(pg_cnt)) * 100)))

        if pg_num != pg_cnt:
            title = f'Page {pg_num} of {pg_cnt} processed ({pct}% completed)'
            subtitle = progress_bar(count)
            wf.add_item(valid=True, title=title, subtitle=subtitle)
        else:
            wf.rerun = 0  # Stop re-running.
            title = f'Page {pg_cnt} of {pg_cnt} processed (100% completed)'
            wf.add_item(valid=True, title=title, icon='checkmark.png')
            wf.clear_cache()

    count += 1

    wf.setvar('count', count)

    wf.send_feedback()


def progress_bar(count):
    """Generate progress bar."""
    bar = [u'\u25CB'] * 5
    i = count % 5
    bar[i] = u'\u25CF'
    return u''.join(bar)


def encrypt(pwd, pdf_paths):
    """Encrypt PDF files.

    Args:
        pwd (str): Password used in the encryption.
        pdf_paths (list): Paths to selected PDF files.
    """
    try:
        for pdf_path in pdf_paths:
            with Pdf.open(pdf_path) as f:
                pdf = Pdf.new()
                pdf.pages.extend(f.pages)
                encryption = Encryption(owner=pwd, user=pwd)
                noextpath = os.path.splitext(pdf_path)[0]
                pdf.save(f'{noextpath} [encrypted].pdf', encryption=encryption)

        notify.notify(
            'Alfred PDF Tools',
            'Encryption successfully completed.'
            )
    except PasswordError:
        notify.notify(
            'Alfred PDF Tools',
            'The PDF file is already encrypted.'
        )


def decrypt(pwd, pdf_paths):
    """Decrypt PDF files.

    Args:
        pwd (str): Password used in the decryption.
        pdf_paths (list): Paths to selected PDF files.
    """
    try:
        for pdf_path in pdf_paths:
            with Pdf.open(pdf_path, password=pwd) as f:
                pdf = Pdf.new()
                pdf.pages.extend(f.pages)
                noextpath = os.path.splitext(pdf_path)[0]
                pdf.save(f'{noextpath} [decrypted].pdf')

                notify.notify(
                    'Alfred PDF Tools',
                    'Decryption successfully completed.'
                )
    except PasswordError:
        notify.notify(
            'Alfred PDF Tools',
            'The entered password is not valid.'
        )


def merge(out_filename, pdf_paths, should_trash):
    """Merge PDF files.

    Args:
        out_filename (str): Filename of the output PDF file.
        pdf_paths (list): Paths to selected PDF files.
        should_trash (bool): `True` for moving the input PDF files to Trash.
    """
    try:
        parent_paths = [Path(pdf_path).parent for pdf_path in pdf_paths]

        if len(pdf_paths) < 2:
            raise SelectionError

        if not parent_paths[1:] == parent_paths[:-1]:
            raise MultiplePathsError

        pdf = Pdf.new()

        for f in pdf_paths:
            src = Pdf.open(f)
            pdf.pages.extend(src.pages)

        if should_trash:
            for pdf_path in pdf_paths:
                send2trash(pdf_path)

        pdf.save(f'{parent_paths[0]}/{out_filename}.pdf')

    except SelectionError:
        notify.notify(
            'Alfred PDF Tools',
            'You must select at least two PDF files to merge.'
        )
    except MultiplePathsError:
        notify.notify(
            'Alfred PDF Tools',
            'Cannot merge PDF files from multiple paths.'
        )
    except PasswordError:
        notify.notify(
            'Alfred PDF Tools',
            'Merge action cannot handle an encrypted PDF file.'
        )


def split_count(max_pages, abs_path, suffix):
    """Split PDF file by page count.

    Args:
        max_pages (str): Maximum amount of pages for each output PDF file.
        abs_path (str): Absolute path of the input PDF file.
        suffix (str): Suffix for the output filenames.
    """
    try:
        if not max_pages.lstrip('+-').isdigit():
            raise NotIntegerError

        if int(max_pages) < 0:
            raise NegativeValueError

        inp_file = Pdf.open(abs_path)
        noextpath = os.path.splitext(abs_path)[0]

        pg_cnt = int(max_pages)
        num_pages = len(inp_file.pages)

        page_ranges = [
            inp_file.pages[n:n + pg_cnt] for n in range(0, num_pages, pg_cnt)
        ]

        for n, page_range in enumerate(page_ranges, 1):
            out_file = Pdf.new()
            out_file.pages.extend(page_range)
            out_file.save(f'{noextpath} [{suffix} {n}].pdf')

    except NotIntegerError:
        notify.notify(
            'Alfred PDF Tools',
            'The argument is not an integer.'
        )
    except NegativeValueError:
        notify.notify(
            'Alfred PDF Tools',
            'Negative integer is not a valid argument.'
        )
    except ZeroDivisionError:
        notify.notify(
            'Alfred PDF Tools',
            'Zero is not a valid argument.'
        )
    except PasswordError:
        notify.notify(
            'Alfred PDF Tools',
            'Split action cannot handle an encrypted PDF file.'
        )


def split_size(max_size, abs_path, suffix):
    """Split PDF file by file size.

    Args:
        max_size (str): Maximum file size for each output PDF file.
        abs_path (str): Absolute path of the input PDF file.
        suffix (str): Suffix for the output filenames.
    """
    try:
        if float(max_size) < 0:
            raise ValueError

        max_chunk_sz = float(max_size) * 1000000
        noextpath = os.path.splitext(abs_path)[0]

        inp_file = Pdf.open(abs_path)
        pg_cnt = len(inp_file.pages)

        pg_sizes = []

        tmp_dir = tempfile.TemporaryDirectory()

        for n, page in enumerate(inp_file.pages):
            tmp_file = Pdf.new()
            tmp_file.pages.append(page)
            tmp_file.save(f'{tmp_dir.name}/page{n}')
            tmp_file_size = os.path.getsize(f'{tmp_dir.name}/page{n}')
            pg_sizes.append(tmp_file_size)
            tmp_file.close()

        inp_file_size = os.path.getsize(abs_path)
        sum_pg_sizes = sum(pg_sizes)
        dividend = min(inp_file_size, sum_pg_sizes)
        divisor = max(inp_file_size, sum_pg_sizes)
        quotient = dividend / divisor

        start = 0
        stop = 1
        pg_num = 0

        if quotient > 0.95:
            pg_chunks = [[(0, pg_sizes.pop(0))]]

            for n, pg_size in enumerate(pg_sizes, 1):
                if sum(ps for _, ps in pg_chunks[-1]) + pg_size < max_chunk_sz:
                    pg_chunks[-1].append((n, pg_size))
                else:
                    pg_chunks.append([(n, pg_size)])

            slices = [slice(n[0][0], n[-1][0] + 1) for n in pg_chunks]

            for n, sl in enumerate(slices, 1):
                out_file = Pdf.new()
                out_file.pages.extend(inp_file.pages[sl])
                out_file.save(f'{noextpath} [{suffix} {n}].pdf')
        else:
            while not stop > pg_cnt:
                out_file_name = f'{noextpath} [{suffix} {pg_num + 1}].pdf'
                chunk = pg_sizes[start:stop]
                chunk_size = sum(chunk)
                chunk_pg_cnt = len(chunk)

                if chunk_size < max_chunk_sz:
                    if stop != pg_cnt:
                        stop += 1
                    else:
                        out_file = Pdf.new()
                        out_file.pages.extend(inp_file.pages[start:stop])
                        out_file.save(out_file_name)
                        break
                else:
                    if chunk_pg_cnt == 1:
                        out_file = Pdf.new()
                        out_file.pages.extend(inp_file.pages[start:stop])
                        out_file.save(out_file_name)
                        start = stop
                        stop += 1
                        pg_num += 1
                    else:
                        stop -= 1
                        out_file = Pdf.new()
                        out_file.pages.extend(inp_file.pages[start:stop])
                        out_file.save(out_file_name)
                        chunk_size = os.path.getsize(out_file_name)
                        next_page = pg_sizes[stop:stop + 1][0]

                        if chunk_size + next_page < max_chunk_sz:
                            os.remove(out_file_name)
                            chunk_size_real = chunk_size / (stop - start)

                            pg_sizes_real = []

                            for i in range(pg_cnt):
                                if i >= start and i < stop:
                                    pg_sizes_real.append(chunk_size_real)
                                else:
                                    pg_sizes_real.append(pg_sizes[i])

                            pg_sizes = pg_sizes_real
                            stop += 1
                        else:
                            start = stop
                            stop += 1
                            pg_num += 1

        inp_file.close()
    except ValueError:
        notify.notify(
            'Alfred PDF Tools',
            'The argument must be a positive numeric value.'
        )
    except PasswordError:
        notify.notify(
            'Alfred PDF Tools',
            'Split action cannot handle an encrypted PDF file.'
        )


def slice_(query, abs_path, is_single, suffix):
    """Slice PDF files.

    Args:
        query (str): Syntax indicating page numbers and/or page ranges.
        abs_path (str): Absolute path of the input PDF file.
        is_single (bool): `True` for a single output file.
        suffix (str): Suffix for the output filenames.
    """
    try:
        inp_file = Pdf.open(abs_path)

        pages = [x.strip() for x in query.split(',')]

        for page in pages:
            if not page.replace('-', '').isdigit():
                raise SyntaxError

        for page in pages:
            if '-' in page:
                if page.split('-')[1]:
                    stop = int(page.split('-')[1])
                else:
                    stop = len(inp_file.pages)
            else:
                stop = int(page)

            if stop > len(inp_file.pages):
                raise IndexError

        noextpath = os.path.splitext(abs_path)[0]

        if is_single:
            out_file = Pdf.new()

            for page in pages:
                if '-' in page:
                    start = int(page.split('-')[0]) - 1

                    if page.split('-')[1]:
                        stop = int(page.split('-')[1])
                    else:
                        stop = len(inp_file.pages)

                    if start == -1:
                        raise StartValueZeroError

                    if start >= stop:
                        raise StartValueReverseError
                else:
                    start = int(page) - 1
                    stop = int(page)

                out_file.pages.extend(inp_file.pages[start:stop])
            out_file.save(f'{noextpath} [sliced].pdf')
        else:
            for part_num, page in enumerate(pages, 1):
                out_file = Pdf.new()

                if '-' in page:
                    start = int(page.split('-')[0]) - 1

                    if page.split('-')[1]:
                        stop = int(page.split('-')[1])
                    else:
                        stop = len(inp_file.pages)

                    if start == -1:
                        raise StartValueZeroError

                    if start >= stop:
                        raise StartValueReverseError
                else:
                    start = int(page) - 1
                    stop = int(page)

                out_file.pages.extend(inp_file.pages[start:stop])
                out_file.save(f'{noextpath} [{suffix} {part_num}].pdf')
    except SyntaxError:
        notify.notify(
            'Alfred PDF Tools',
            'The input syntax is not valid.'
        )
    except IndexError:
        notify.notify(
            'Alfred PDF Tools',
            'Page number out of range.'
        )
    except StartValueZeroError:
        notify.notify(
            'Alfred PDF Tools',
            'Page number cannot be zero.'
        )
    except StartValueReverseError:
        notify.notify(
            'Alfred PDF Tools',
            'You cannot set a page range in reverse order.'
        )
    except PasswordError:
        notify.notify(
            'Alfred PDF Tools',
            'Slice action cannot handle an encrypted PDF file.'
        )


def crop(pdf_paths):
    """Crop two-column pages.

    Args:
        pdf_paths (list): Paths to selected PDF files.
    """
    try:
        for pdf_path in pdf_paths:
            inp_file = Pdf.open(pdf_path)
            out_file = Pdf.new()

            for page in inp_file.pages:
                for _ in range(2):
                    out_file.pages.append(out_file.copy_foreign(page))

            for i, page in enumerate(out_file.pages, 1):
                x1, y1, x2, y2 = page.MediaBox
                middle = x1 + (x2 - x1) / 2

                if i % 2:  # Check if the page is even.
                    x2 = middle
                else:
                    x1 = middle

                page.MediaBox = [x1, y1, x2, y2]

            noextpath = os.path.splitext(pdf_path)[0]
            out_file.save(f'{noextpath} [cropped].pdf')
    except PasswordError:
        notify.notify(
            'Alfred PDF Tools',
            'Slice action cannot handle an encrypted PDF file.'
        )


def scale(pdf_paths):
    """Scale PDF files to a given page size.

    Args:
        pdf_paths (list): Paths to selected PDF files.
    """
    try:
        width = float(os.environ['width']) * 72
        height = float(os.environ['height']) * 72

        for pdf_path in pdf_paths:
            inp_file = Pdf.open(pdf_path)
            out_file = Pdf.new()

            for i, page in enumerate(inp_file.pages):
                out_file.add_blank_page(page_size=(width, height))
                out_file.pages[i].add_overlay(page)

            noextpath = os.path.splitext(pdf_path)[0]
            out_file.save(f'{noextpath} [scaled].pdf')
    except PasswordError:
        notify.notify(
            'Alfred PDF Tools',
            'Scale action cannot handle an encrypted PDF file.'
        )


def main(wf):
    """Run workflow."""
    args = docopt(__doc__)
    query = wf.args[1]
    abs_path = os.environ['abs_path']
    pdf_paths = abs_path.split('\t')
    suffix = os.environ['suffix']

    if args.get('--optimize'):
        optimize(query, pdf_paths)
    elif args.get('--deskew'):
        deskew(pdf_paths)
    elif args.get('--progress'):
        get_progress()
    elif args.get('--encrypt'):
        encrypt(query, pdf_paths)
    elif args.get('--decrypt'):
        decrypt(query, pdf_paths)
    elif args.get('--mrg'):
        merge(query, pdf_paths, False)
    elif args.get('--mrg-trash'):
        merge(query, pdf_paths, True)
    elif args.get('--split-count'):
        split_count(query, abs_path, suffix)
    elif args.get('--split-size'):
        split_size(query, abs_path, suffix)
    elif args.get('--slice-multi'):
        slice_(query, abs_path, False, suffix)
    elif args.get('--slice-single'):
        slice_(query, abs_path, True, suffix)
    elif args.get('--crop'):
        crop(pdf_paths)
    elif args.get('--scale'):
        scale(pdf_paths)

    if wf.update_available:
        notify.notify(
            'Alfred PDF Tools',
            'A newer version of the workflow is available.',
            'Glass'
        )
        wf.start_update()


if __name__ == '__main__':
    wf = Workflow(update_settings=UPDATE_SETTINGS, help_url=HELP_URL)
    sys.exit(wf.run(main))
