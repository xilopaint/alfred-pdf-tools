#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2017 Arthur Pinheiro
#
# MIT Licence. See http://opensource.org/licenses/MIT

"""
Optimize, encrypt and manipulate PDF files.

Usage:
    alfred_pdf_tools.py optimize <query>
    alfred_pdf_tools.py progress <query>
    alfred_pdf_tools.py encrypt <query>
    alfred_pdf_tools.py decrypt <query>
    alfred_pdf_tools.py mrg <query>
    alfred_pdf_tools.py mrgtrash <query>
    alfred_pdf_tools.py splitcount <query>
    alfred_pdf_tools.py splitsize <query>
    alfred_pdf_tools.py slicemulti <query>
    alfred_pdf_tools.py slicesingle <query>

Commands:
    optimize <query>      Optimize PDF files.
    progress <query>      Track optimization progress.
    encrypt <query>       Encrypt PDF files.
    decrypt <query>       Decrypt PDF files.
    mrg <query>           Merge PDF files.
    mrgtrash <query>      Merge PDF files and move them to trash.
    splitcount <query>    Split PDF file by page count.
    splitsize <query>     Split PDF file by file size.
    slicemulti <query>    Multi-slice PDF files.
    slicesingle <query>   Single-slice PDF files.
"""

from __future__ import division
import sys
import os
from docopt import docopt
from workflow import Workflow3, notify, ICON_WARNING
from subprocess import Popen, PIPE
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter, PdfReadError
from send2trash import send2trash


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


def optimize(query, f, c):
    """Optimize PDF files."""
    try:
        if query:
            if not query.lstrip('+-').isdigit():
                raise NotIntegerError

        if query:
            if int(query) < 0:
                raise NegativeValueError

        for i in xrange(c):
            command = "echo -y | ./k2pdfopt '{}' -as -mode copy -dpi {} -o '%s (optimized).pdf' -x".format(f[i], query)
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
    bar[i] = u'\u25CF'
    return u''.join(bar)


def encrypt(query, f, c):
    """Encrypt PDF files."""
    noextpath = [os.path.splitext(x) for x in f]

    for n in xrange(c):
        inp_file = open(f[n], 'rb')
        reader = PdfFileReader(inp_file, strict=False)

        if not reader.isEncrypted:
            writer = PdfFileWriter()

            for pg_no in range(reader.numPages):
                writer.addPage(reader.getPage(pg_no))

            writer.encrypt(query)
            out_file = open(noextpath[n][0] + ' (encrypted).pdf', 'wb')
            writer.write(out_file)
            notify.notify('Alfred PDF Tools',
                          'Encryption successfully completed.')
        else:
            notify.notify('Alfred PDF Tools',
                          'The PDF file is already encrypted.')


def decrypt(query, f, c):
    """Decrypt PDF files."""
    noextpath = [os.path.splitext(x) for x in f]

    try:
        for n in xrange(c):
            inp_file = open(f[n], 'rb')
            reader = PdfFileReader(inp_file, strict=False)

            if reader.isEncrypted:
                reader.decrypt(query)
                writer = PdfFileWriter()

                for pg_no in range(reader.numPages):
                    writer.addPage(reader.getPage(pg_no))

                out_file = open(noextpath[n][0] + ' (decrypted).pdf', 'wb')
                writer.write(out_file)
                notify.notify('Alfred PDF Tools',
                              'Decryption successfully completed.')

            else:
                notify.notify('Alfred PDF Tools',
                              'The PDF file is not encrypted.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'The entered password is not valid.')


def merge(query, f, c, trash):
    """Merge PDF files."""
    paths = [os.path.split(path)[0] for path in f]
    merger = PdfFileMerger(strict=False)

    try:
        if c < 2:
            raise SelectionError

        if not paths[1:] == paths[:-1]:
            raise MultiplePathsError

        for pdf in f:
            reader = PdfFileReader(open(pdf, 'rb'))
            merger.append(reader)

        if trash:
            for pdf in f:
                send2trash(pdf)

        merger.write(paths[0] + "/" + query + ".pdf")

    except SelectionError:
        notify.notify('Alfred PDF Tools',
                      'You must select at least two PDF files to merge.')

    except MultiplePathsError:
        notify.notify('Alfred PDF Tools',
                      'Cannot merge PDF files from multiple paths.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'Merge action cannot handle an encrypted PDF file.')


def split_count(query, abs_path):
    """Split PDF file by page count"""
    try:
        if not query.lstrip("+-").isdigit():
            raise NotIntegerError

        if int(query) < 0:
            raise NegativeValueError

        page_count = int(query)
        start = 0
        stop = page_count
        inp_file = open(abs_path, 'rb')
        reader = PdfFileReader(inp_file)
        num_pages = int(reader.getNumPages())
        quotient = num_pages / page_count

        if quotient.is_integer():
            for i in xrange(int(quotient)):
                merger = PdfFileMerger(strict=False)
                merger.append(inp_file, pages=(start, stop))
                noextpath = os.path.splitext(abs_path)[0]
                merger.write(noextpath + (' (part {}).pdf').format(i + 1))
                start = stop
                stop = start + page_count

        else:
            for i in xrange(int(quotient) + 1):
                merger = PdfFileMerger(strict=False)
                merger.append(inp_file, pages=(start, stop))
                noextpath = os.path.splitext(abs_path)[0]
                merger.write(noextpath + (' (part {}).pdf').format(i + 1))
                if i != int(quotient) - 1:
                    start = stop
                    stop = start + page_count
                else:
                    start = int(quotient) * page_count
                    stop = num_pages

    except NotIntegerError:
        notify.notify('Alfred PDF Tools', 'The argument is not an integer.')

    except NegativeValueError:
        notify.notify('Alfred PDF Tools',
                      'Negative integer is not a valid argument.')

    except ZeroDivisionError:
        notify.notify('Zero is not a valid argument.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'Split action cannot handle an encrypted PDF file.')


def split_size(query, abs_path):
    """Split PDF file by file size."""
    try:
        arg_file_size = float(query) * 1000000
        noextpath = os.path.splitext(abs_path)[0]
        inp_file = open(abs_path, 'rb')
        reader = PdfFileReader(inp_file)
        pg_cnt = int(reader.getNumPages())
        start = 0
        stop = 1
        pg_no = 0

        while start < pg_cnt:
            merger = PdfFileMerger(strict=False)
            merger.append(inp_file, pages=(start, stop))
            merger.write(noextpath)
            obj_path = noextpath
            obj = PdfFileReader(open(obj_path, 'rb'))
            num_pages_obj = int(obj.getNumPages())
            file_size = os.path.getsize(obj_path)
            os.remove(obj_path)

            if file_size < arg_file_size:
                if stop == pg_cnt:
                    merger = PdfFileMerger(strict=False)
                    merger.append(inp_file, pages=(start, stop))
                    merger.write(noextpath +
                                 (' (part {}).pdf').format(pg_no + 1))
                    break
                else:
                    stop = stop + 1

            else:
                if num_pages_obj == 1:
                    merger = PdfFileMerger(strict=False)
                    merger.append(inp_file, pages=(start, stop))
                    merger.write(noextpath +
                                 (' (part {}).pdf').format(pg_no + 1))
                    start = stop
                    stop = stop + 1
                    pg_no = pg_no + 1

                else:
                    stop = stop - 1
                    merger = PdfFileMerger(strict=False)
                    merger.append(inp_file, pages=(start, stop))
                    merger.write(noextpath +
                                 (' (part {}).pdf').format(pg_no + 1))
                    start = stop
                    stop = stop + 1
                    pg_no = pg_no + 1

    except ValueError:
        notify.notify('Alfred PDF Tools',
                      'The argument must be a positive numeric value.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'Split action cannot handle an encrypted PDF file.')


def slice_(query, abs_path, single):
    """Slice PDF files."""
    try:
        pages = [x.strip() for x in query.split(',')]
        page = [x.split('-') for x in pages]
        inp_file = open(abs_path, 'rb')
        reader = PdfFileReader(inp_file)
        pg_cnt = reader.getNumPages()

        for n in xrange(len(pages)):
            if pages[n].replace('-', '').isdigit():
                pass

            else:
                raise SyntaxError

        for n in xrange(len(pages)):
            if "-" in pages[n]:
                stop = int(page[n][1])
                if stop > pg_cnt:
                    raise IndexError
                else:
                    pass

            else:
                stop = int(pages[n])
                if stop > pg_cnt:
                    raise IndexError
                else:
                    pass

        noextpath = os.path.splitext(abs_path)[0]

        if single:
            merger = PdfFileMerger(strict=False)
            inp_file = open(abs_path, 'rb')
            reader = PdfFileReader(inp_file)

            for n in xrange(len(pages)):
                if "-" in pages[n]:
                    start = int(page[n][0]) - 1
                    stop = int(page[n][1])

                    if start == -1:
                        raise StartValueZeroError

                    if start >= stop:
                        raise StartValueReverseError

                    merger.append(reader, pages=(start, stop))

                else:
                    start = int(pages[n]) - 1
                    stop = int(pages[n])
                    merger.append(reader, pages=(start, stop))

            merger.write(noextpath + ' (slice).pdf')

        else:
            for n in xrange(len(pages)):
                if "-" in pages[n]:
                    merger = PdfFileMerger(strict=False)
                    inp_file = open(abs_path, 'rb')
                    reader = PdfFileReader(inp_file)
                    start = int(page[n][0]) - 1
                    stop = int(page[n][1])

                    if start == -1:
                        raise StartValueZeroError

                    if start >= stop:
                        raise StartValueReverseError

                    merger.append(reader, pages=(start, stop))
                    merger.write(noextpath + (' (part {}).pdf').format(n + 1))

                else:
                    merger = PdfFileMerger(strict=False)
                    reader = PdfFileReader(open(abs_path, 'rb'))
                    start = int(pages[n]) - 1
                    stop = int(pages[n])
                    merger.append(reader, pages=(start, stop))
                    merger.write(noextpath + (' (part {}).pdf').format(n + 1))

    except SyntaxError:
        notify.notify('Alfred PDF Tools', 'The input syntax is not valid.')

    except IndexError:
        notify.notify('Alfred PDF Tools', 'Page number out of range.')

    except StartValueZeroError:
        notify.notify('Alfred PDF Tools', 'Page number cannot be zero.')

    except StartValueReverseError:
        notify.notify('Alfred PDF Tools',
                      'You cannot set a page range in reverse order.')

    except PdfReadError:
        notify.notify('Alfred PDF Tools',
                      'Slice action cannot handle an encrypted PDF file.')


def main(wf):
    """Run workflow."""
    args = docopt(__doc__, wf.args)
    query = wf.args[1].encode('utf-8')
    abs_path = os.environ['abs_path']
    f = abs_path.split('\t')
    c = len(f)
    print query

    if args.get('optimize'):
        optimize(query, f, c)

    elif args.get('progress'):
        get_progress()

    elif args.get('encrypt'):
        encrypt(query, f, c)

    elif args.get('decrypt'):
        decrypt(query, f, c)

    elif args.get('mrg'):
        merge(query, f, c, False)

    elif args.get('mrgtrash'):
        merge(query, f, c, True)

    elif args.get('splitcount'):
        split_count(query, abs_path)

    elif args.get('splitsize'):
        split_size(query, abs_path)

    elif args.get('slicemulti'):
        slice_(query, abs_path, False)

    elif args.get('slicesingle'):
        slice_(query, abs_path, True)

    if wf.update_available:
        notify.notify('Alfred PDF Tools',
                      'A newer version of the workflow is available.',
                      'Glass')
        wf.start_update()


if __name__ == '__main__':
    wf = Workflow3(update_settings=UPDATE_SETTINGS)
    sys.exit(wf.run(main))
