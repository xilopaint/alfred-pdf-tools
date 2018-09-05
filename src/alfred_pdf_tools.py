#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2017 Arthur Pinheiro
#
# MIT Licence. See http://opensource.org/licenses/MIT

"""
Usage:
    alfred_pdf_tools.py --optimize <query>
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
    alfred_pdf_tools.py --suffix <query>

Optimize, encrypt and manipulate PDF files.

Options:
    [--optimize <query>]    Optimize PDF files.
    --progress              Track optimization progress.
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
    --suffix <query>        Set new value to the "suffix" environment variable.
"""

from __future__ import division
import sys
import os
from docopt import docopt
from workflow import Workflow3, notify, util, ICON_WARNING
from subprocess import Popen, PIPE
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter, PdfReadError
from PyPDF2.pdf import PageObject
from send2trash import send2trash
import tempfile
from copy import copy
from math import floor


UPDATE_SETTINGS = {'github_slug': 'xilopaint/alfred-pdf-tools'}


class AlfredPdfToolsError(Exception):
    """Creates Subclass of Exception class."""
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


class FileEncryptedError(AlfredPdfToolsError):
    """Raised when a file action cannot handle an encrypted file."""
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


class SuffixNotSetError(AlfredPdfToolsError):
    """Raised when the PDF files suffix cannot be set."""


def optimize(query, pdfs):
    """Optimize PDF files."""
    try:
        if query:
            if not query.lstrip('+-').isdigit():
                raise NotIntegerError

        if query:
            if int(query) < 0:
                raise NegativeValueError

        for pdf in pdfs:
            command = "echo -y | ./k2pdfopt '{}' -as -mode copy -dpi {} -o '%s (optimized).pdf' -x".format(pdf, query)
            proc = Popen(command, shell=True, stdout=PIPE)

            while proc.poll() is None:
                line = proc.stdout.readline()

                if "Reading" in line:
                    pg_cnt = line.split()
                    wf.cache_data('page_count', pg_cnt[1])

                if "SOURCE PAGE" in line:
                    pg_no = line.split()
                    wf.cache_data('page_number', pg_no[2])

            notify.notify('Alfred PDF Tools',
                          'Optimization successfully completed.')

    except NotIntegerError:
        notify.notify('Alfred PDF Tools',
                      'The argument is not an integer.')

    except NegativeValueError:
        notify.notify('Alfred PDF Tools',
                      'Negative integer is not a valid argument.')


def get_progress():
    """Show optimization progress."""
    pg_no = wf.cached_data('page_number', max_age=10)
    pg_cnt = wf.cached_data('page_count', max_age=0)

    wf.rerun = 1

    try:
        n = int(os.environ['n'])

    except KeyError:
        n = 0

    if not pg_no:
        if wf.cached_data_age('page_count') < 10:
            title = "Reading the PDF file..."
            subtitle = progress_bar(n)
            wf.add_item(valid=True, title=title, subtitle=subtitle)

        else:
            title = "Optimize action is not running."
            wf.add_item(valid=True, title=title, icon=ICON_WARNING)

    else:
        prog_int = int(round((float(pg_no) / float(pg_cnt)) * 100))
        prog = str(prog_int)

        if pg_no != pg_cnt:
            title = "Page {} of {} processed ({}% completed)".format(pg_no,
                                                                     pg_cnt,
                                                                     prog)
            subtitle = progress_bar(n)
            wf.add_item(valid=True, title=title, subtitle=subtitle)

        else:
            title = "Page {} of {} processed ({}% completed)".format(pg_no,
                                                                     pg_cnt,
                                                                     prog)
            wf.add_item(valid=True, title=title, icon='checkmark.png')

    n += 1

    wf.setvar('n', n)

    wf.send_feedback()


def progress_bar(n):
    """Generate progress bar."""
    bar = [u'\u25CB'] * 5
    i = n % 5
    bar[i] = u"\u25CF"
    return u"".join(bar)


def encrypt(query, pdfs):
    """Encrypt PDF files."""
    for pdf in pdfs:
        reader = PdfFileReader(pdf, strict=False)

        if not reader.isEncrypted:
            writer = PdfFileWriter()

            for i in xrange(reader.numPages):
                writer.addPage(reader.getPage(i))

            writer.encrypt(query)
            noextpath = os.path.splitext(pdf)[0]
            out_file = "{} (encrypted).pdf".format(noextpath)

            with open(out_file, 'wb') as f:
                writer.write(f)

            notify.notify('Alfred PDF Tools',
                          'Encryption successfully completed.')
        else:
            notify.notify('Alfred PDF Tools',
                          'The PDF file is already encrypted.')


def decrypt(query, pdfs):
    """Decrypt PDF files."""
    try:
        for pdf in pdfs:
            reader = PdfFileReader(pdf, strict=False)

            if reader.isEncrypted:
                reader.decrypt(query)
                writer = PdfFileWriter()

                for i in xrange(reader.numPages):
                    writer.addPage(reader.getPage(i))

                noextpath = os.path.splitext(pdf)[0]
                out_file = "{} (decrypted).pdf".format(noextpath)

                with open(out_file, 'wb') as f:
                    writer.write(f)

                notify.notify('Alfred PDF Tools',
                              'Decryption successfully completed.')

            else:
                notify.notify('Alfred PDF Tools',
                              'The PDF file is not encrypted.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'The entered password is not valid.')


def merge(query, pdfs, should_trash):
    """Merge PDF files."""
    try:
        paths = [os.path.split(path)[0] for path in pdfs]

        if len(pdfs) < 2:
            raise SelectionError

        if not paths[1:] == paths[:-1]:
            raise MultiplePathsError

        merger = PdfFileMerger(strict=False)

        for pdf in pdfs:
            reader = PdfFileReader(pdf)

            if reader.isEncrypted:
                raise FileEncryptedError

            merger.append(reader)

        if should_trash:
            for pdf in pdfs:
                send2trash(pdf)

        merger.write(paths[0] + '/' + query + '.pdf')

    except SelectionError:
        notify.notify('Alfred PDF Tools',
                      'You must select at least two PDF files to merge.')

    except MultiplePathsError:
        notify.notify('Alfred PDF Tools',
                      'Cannot merge PDF files from multiple paths.')

    except FileEncryptedError:
        notify.notify('Alfred PDF Tools',
                      'Merge action cannot handle an encrypted PDF file.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'Cannot merge a malformed PDF file.')


def split_count(query, abs_path, suffix):
    """Split PDF file by page count"""
    try:
        if not query.lstrip('+-').isdigit():
            raise NotIntegerError

        if int(query) < 0:
            raise NegativeValueError

        reader = PdfFileReader(abs_path)

        if reader.isEncrypted:
            raise FileEncryptedError

        pg_cnt = int(query)
        start = 0
        stop = pg_cnt

        writer = PdfFileWriter()

        for i in xrange(reader.numPages):
            writer.addPage(reader.getPage(i))

        tmp_file = tempfile.NamedTemporaryFile()
        writer.removeLinks()
        writer.write(tmp_file)
        reader = PdfFileReader(tmp_file)
        num_pages = int(reader.numPages)
        quotient = num_pages / pg_cnt

        if quotient.is_integer():
            for i in xrange(int(quotient)):
                merger = PdfFileMerger(strict=False)
                merger.append(tmp_file, pages=(start, stop))
                noextpath = os.path.splitext(abs_path)[0]
                out_file = "{} ({} {}).pdf".format(noextpath, suffix, i + 1)
                merger.write(out_file)
                start = stop
                stop = start + pg_cnt

        else:
            for i in xrange(int(quotient) + 1):
                merger = PdfFileMerger(strict=False)
                merger.append(tmp_file, pages=(start, stop))
                noextpath = os.path.splitext(abs_path)[0]
                out_file = "{} ({} {}).pdf".format(noextpath, suffix, i + 1)
                merger.write(out_file)

                if i != int(quotient) - 1:
                    start = stop
                    stop = start + pg_cnt
                else:
                    start = int(quotient) * pg_cnt
                    stop = num_pages

        tmp_file.close()

    except NotIntegerError:
        notify.notify('Alfred PDF Tools', 'The argument is not an integer.')

    except NegativeValueError:
        notify.notify('Alfred PDF Tools',
                      'Negative integer is not a valid argument.')

    except ZeroDivisionError:
        notify.notify('Alfred PDF Tools', 'Zero is not a valid argument.')

    except FileEncryptedError:
        notify.notify('Alfred PDF Tools',
                      'Split action cannot handle an encrypted PDF file.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'Cannot split a malformed PDF file.')


def split_size(query, abs_path, suffix):
    """Split PDF file by file size."""
    try:
        if float(query) < 0:
            raise ValueError

        max_part_size = float(query) * 1000000
        noextpath = os.path.splitext(abs_path)[0]
        reader = PdfFileReader(abs_path, strict=False)
        pg_cnt = reader.numPages

        if reader.isEncrypted:
            raise FileEncryptedError

        pg_sizes = []

        for i in xrange(pg_cnt):
            writer = PdfFileWriter()
            writer.addPage(reader.getPage(i))
            writer.removeLinks()
            tmp_file = tempfile.NamedTemporaryFile()
            writer.write(tmp_file)
            file_size = os.path.getsize(tmp_file.name)
            pg_sizes.append(file_size)
            tmp_file.close()

        writer = PdfFileWriter()

        for i in xrange(pg_cnt):
            writer.addPage(reader.getPage(i))

        inp_file = tempfile.NamedTemporaryFile()
        writer.write(inp_file)

        inp_file_size = os.path.getsize(abs_path)
        sum_pg_sizes = sum(pg_sizes)
        dividend = min(inp_file_size, sum_pg_sizes)
        divisor = max(inp_file_size, sum_pg_sizes)
        quotient = dividend / divisor

        start = 0
        stop = 1
        pg_no = 0

        while not stop > pg_cnt:
            out_file = '{} ({} {}).pdf'.format(noextpath, suffix, pg_no + 1)

            if quotient > 0.95:
                part = pg_sizes[start:stop]
                part_size = sum(part)
                part_pg_cnt = len(part)

                if part_size < max_part_size:
                    if stop != pg_cnt:
                        stop += 1

                    else:
                        merger = PdfFileMerger(strict=False)
                        merger.append(inp_file, pages=(start, stop))
                        merger.write(out_file)
                        break

                else:
                    if part_pg_cnt == 1:
                        merger = PdfFileMerger(strict=False)
                        merger.append(inp_file, pages=(start, stop))
                        merger.write(out_file)
                        start = stop
                        stop += 1
                        pg_no += 1

                    else:
                        stop -= 1
                        merger = PdfFileMerger(strict=False)
                        merger.append(inp_file, pages=(start, stop))
                        merger.write(out_file)
                        start = stop
                        stop += 1
                        pg_no += 1

            else:
                part = pg_sizes[start:stop]
                part_size = sum(part)
                part_pg_cnt = len(part)

                if part_size < max_part_size:
                    if stop != pg_cnt:
                        stop += 1

                    else:
                        merger = PdfFileMerger(strict=False)
                        merger.append(inp_file, pages=(start, stop))
                        merger.write(out_file)
                        break

                else:
                    if part_pg_cnt == 1:
                        merger = PdfFileMerger(strict=False)
                        merger.append(inp_file, pages=(start, stop))
                        merger.write(out_file)
                        start = stop
                        stop += 1
                        pg_no += 1

                    else:
                        stop -= 1
                        merger = PdfFileMerger(strict=False)
                        merger.append(inp_file, pages=(start, stop))
                        merger.write(out_file)
                        part_size = os.path.getsize(out_file)
                        next_page = pg_sizes[stop:stop + 1][0]

                        if part_size + next_page < max_part_size:
                            os.remove(out_file)
                            part_size_real = part_size / (stop - start)

                            pg_sizes_real = []

                            for i in xrange(pg_cnt):
                                if i >= start and i < stop:
                                    pg_sizes_real.append(part_size_real)

                                else:
                                    pg_sizes_real.append(pg_sizes[i])

                            pg_sizes = pg_sizes_real
                            stop += 1

                        else:
                            start = stop
                            stop += 1
                            pg_no += 1

        inp_file.close()

    except ValueError:
        notify.notify('Alfred PDF Tools',
                      'The argument must be a positive numeric value.')

    except FileEncryptedError:
        notify.notify('Alfred PDF Tools',
                      'Split action cannot handle an encrypted PDF file.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'Cannot split a malformed PDF file.')


def slice_(query, abs_path, single, suffix):
    """Slice PDF files."""
    try:
        reader = PdfFileReader(abs_path)

        if reader.isEncrypted:
            raise FileEncryptedError

        writer = PdfFileWriter()

        for i in xrange(reader.numPages):
            writer.addPage(reader.getPage(i))

        tmp_file = tempfile.NamedTemporaryFile()
        writer.removeLinks()
        writer.write(tmp_file)
        reader = PdfFileReader(tmp_file)

        pages = [x.strip() for x in query.split(',')]

        for page in pages:
            if not page.replace('-', '').isdigit():
                raise SyntaxError

        for page in pages:
            if "-" in page:
                if page.split('-')[1]:
                    stop = int(page.split('-')[1])
                else:
                    stop = reader.numPages

            else:
                stop = int(page)

            if stop > reader.numPages:
                raise IndexError

        noextpath = os.path.splitext(abs_path)[0]

        if single:
            merger = PdfFileMerger(strict=False)

            for page in pages:
                if "-" in page:
                    start = int(page.split('-')[0]) - 1
                    stop_str = page.split('-')[1]

                    if stop_str:
                        stop = int(stop_str)
                    else:
                        stop = reader.numPages

                    if start == -1:
                        raise StartValueZeroError

                    if start >= stop:
                        raise StartValueReverseError

                else:
                    start = int(page) - 1
                    stop = int(page)

                merger.append(reader, pages=(start, stop))

            merger.write(noextpath + ' (sliced).pdf')

        else:
            part_no = 0

            for page in pages:
                merger = PdfFileMerger(strict=False)

                if "-" in page:
                    start = int(page.split('-')[0]) - 1
                    stop_str = page.split('-')[1]

                    if stop_str:
                        stop = int(stop_str)
                    else:
                        stop = reader.numPages

                    if start == -1:
                        raise StartValueZeroError

                    if start >= stop:
                        raise StartValueReverseError

                else:
                    start = int(page) - 1
                    stop = int(page)

                out_file = '{} ({} {}).pdf'.format(noextpath,
                                                   suffix,
                                                   part_no + 1)
                merger.append(reader, pages=(start, stop))
                merger.write(out_file)
                part_no += 1

        tmp_file.close()

    except SyntaxError:
        notify.notify('Alfred PDF Tools', 'The input syntax is not valid.')

    except IndexError:
        notify.notify('Alfred PDF Tools', 'Page number out of range.')

    except StartValueZeroError:
        notify.notify('Alfred PDF Tools', 'Page number cannot be zero.')

    except StartValueReverseError:
        notify.notify('Alfred PDF Tools',
                      'You cannot set a page range in reverse order.')

    except FileEncryptedError:
        notify.notify('Alfred PDF Tools',
                      'Slice action cannot handle an encrypted PDF file.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'Cannot slice a malformed PDF file.')


def crop(pdfs):
    """Crop two-column pages."""
    try:
        for pdf in pdfs:
            reader = PdfFileReader(pdf, strict=False)

            if reader.isEncrypted:
                raise FileEncryptedError

            for i in xrange(reader.numPages):
                # Make two copies of the input page.
                pp = reader.getPage(i)
                p = copy(pp)
                q = copy(pp)

                # The new media boxes are the previous crop boxes.
                p.mediaBox = copy(p.cropBox)
                q.mediaBox = copy(p.cropBox)

                x1, x2 = p.mediaBox.lowerLeft
                x3, x4 = p.mediaBox.upperRight

                x1, x2 = floor(x1), floor(x2)
                x3, x4 = floor(x3), floor(x4)
                x5, x6 = x1 + floor((x3 - x1) / 2), x2 + floor((x4 - x2) / 2)

                if (x3 - x1) > (x4 - x2):
                    # Horizontal
                    q.mediaBox.upperRight = (x5, x4)
                    q.mediaBox.lowerLeft = (x1, x2)

                    p.mediaBox.upperRight = (x3, x4)
                    p.mediaBox.lowerLeft = (x5, x2)
                else:
                    # Vertical
                    p.mediaBox.upperRight = (x3, x4)
                    p.mediaBox.lowerLeft = (x1, x6)

                    q.mediaBox.upperRight = (x3, x6)
                    q.mediaBox.lowerLeft = (x1, x2)

                p.artBox = p.mediaBox
                p.bleedBox = p.mediaBox
                p.cropBox = p.mediaBox

                q.artBox = q.mediaBox
                q.bleedBox = q.mediaBox
                q.cropBox = q.mediaBox

                writer = PdfFileWriter()
                writer.addPage(q)
                writer.addPage(p)

                noextpath = os.path.splitext(pdf)[0]
                out_file = '{} (cropped).pdf'.format(noextpath)

                with open(out_file, 'wb') as f:
                    writer.write(f)

    except FileEncryptedError:
        notify.notify('Alfred PDF Tools',
                      'Crop action cannot handle an encrypted PDF file.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'Cannot crop a malformed PDF file.')


def scale(query, pdfs):
    """Scale PDF files to a given page size."""
    try:
        for pdf in pdfs:
            reader = PdfFileReader(pdf, strict=False)

            if reader.isEncrypted:
                raise FileEncryptedError

            writer = PdfFileWriter()

            w, h = [float(i) * 72 for i in query.split('x')]

            for i in xrange(reader.numPages):
                inp_page = reader.getPage(i)

                inp_page_w = float(inp_page.mediaBox[2])
                inp_page_h = float(inp_page.mediaBox[3])

                scale_w = w / inp_page_w
                scale_h = h / inp_page_h
                scale = min(scale_w, scale_h)

                out_page = PageObject.createBlankPage(None, w, h)
                out_page.mergeScaledTranslatedPage(inp_page, scale, 0, 0)

                writer.addPage(out_page)

            noextpath = os.path.splitext(pdf)[0]
            out_file = '{} (scaled).pdf'.format(noextpath)

            with open(out_file, 'wb') as f:
                writer.write(f)

    except FileEncryptedError:
        notify.notify('Alfred PDF Tools',
                      'Scale action cannot handle an encrypted PDF file.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'Cannot scale a malformed PDF file.')


def set_suffix(query):
    """Set new value to the suffix environment variable."""
    try:
        util.set_config('suffix', query, exportable=True)
        notify.notify('Alfred PDF Tools',
                      'Suffix set to "{}".'.format(query))

    except SuffixNotSetError:
        notify.notify('Alfred PDF Tools',
                      'An error occurred while setting the suffix.')


def main(wf):
    """Run workflow."""
    args = docopt(__doc__)
    query = wf.args[1].encode('utf-8')
    abs_path = os.environ['abs_path']
    pdfs = abs_path.split('\t')
    suffix = os.environ['suffix']

    if args.get('--optimize'):
        optimize(query, pdfs)

    elif args.get('--progress'):
        get_progress()

    elif args.get('--encrypt'):
        encrypt(query, pdfs)

    elif args.get('--decrypt'):
        decrypt(query, pdfs)

    elif args.get('--mrg'):
        merge(query, pdfs, False)

    elif args.get('--mrg-trash'):
        merge(query, pdfs, True)

    elif args.get('--split-count'):
        split_count(query, abs_path, suffix)

    elif args.get('--split-size'):
        split_size(query, abs_path, suffix)

    elif args.get('--slice-multi'):
        slice_(query, abs_path, False, suffix)

    elif args.get('--slice-single'):
        slice_(query, abs_path, True, suffix)

    elif args.get('--crop'):
        crop(pdfs)

    elif args.get('--scale'):
        scale(query, pdfs)

    elif args.get('--suffix'):
        set_suffix(query)

    if wf.update_available:
        notify.notify('Alfred PDF Tools',
                      'A newer version of the workflow is available.',
                      'Glass')
        wf.start_update()


if __name__ == '__main__':
    wf = Workflow3(update_settings=UPDATE_SETTINGS)
    sys.exit(wf.run(main))
