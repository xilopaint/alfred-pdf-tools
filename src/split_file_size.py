#!/usr/bin/env python
# encoding: utf-8

import sys
from PyPDF2 import PdfFileMerger, PdfFileReader
import os.path

def main():

    abs_path = os.environ['abs_path']
    query = os.environ['query'].replace(',', '.')
    arg_file_size = float(query)*1000000
    no_ext_path = os.path.splitext(abs_path)[0]

    class AlfredPdfSuiteError(Exception):
        pass

    class NegativeValueError(AlfredPdfSuiteError):
        pass

    try:

        if abs_path == 'more than one file':
            raise MultipleFileError('You cannot select more than one file.')

        if not abs_path.endswith('.pdf'):
            raise NotPdfError('The selected object is not a PDF file.')

        if arg_file_size < 0:
            raise NegativeValueError('Negative value is not a valid argument.')

        inp_file = PdfFileReader(open(abs_path, 'rb'))
        num_pages = int(inp_file.getNumPages())
        start = 0
        stop = 1
        page_number = 0

        while start < num_pages:
            merger = PdfFileMerger()
            merger.append(inp_file, pages=(start, stop))
            merger.write(no_ext_path)
            obj_path = no_ext_path
            obj = PdfFileReader(open(obj_path, 'rb'))
            num_pages_obj = int(obj.getNumPages())
            file_size = os.path.getsize(obj_path)
            os.remove(obj_path)

            if file_size < arg_file_size:
                if stop == num_pages:
                    merger = PdfFileMerger()
                    merger.append(inp_file, pages=(start, stop))
                    merger.write(no_ext_path + (' (part {}).pdf').format(page_number + 1))
                    break
                else:
                    stop = stop + 1

            else:
                if num_pages_obj == 1:
                    merger = PdfFileMerger()
                    merger.append(inp_file, pages=(start, stop))
                    merger.write(no_ext_path + (' (part {}).pdf').format(page_number + 1))
                    start = stop
                    stop = stop + 1
                    page_number = page_number + 1

                else:
                    stop = stop - 1
                    merger = PdfFileMerger()
                    merger.append(inp_file, pages=(start, stop))
                    merger.write(no_ext_path + (' (part {}).pdf').format(page_number + 1))
                    start = stop
                    stop = stop + 1
                    page_number = page_number + 1

    except NegativeValueError as err:
        print err

if __name__ == '__main__':
    sys.exit(main())
