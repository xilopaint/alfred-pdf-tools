#!/usr/bin/python
# encoding: utf-8

from __future__ import division
import sys
import os
from PyPDF2 import PdfFileMerger, PdfFileReader

def main():

    abs_path = os.environ['abs_path']
    query = os.environ['query']

    class AlfredPdfToolsError(Exception):
        pass

    class NotIntegerError(AlfredPdfToolsError):
        pass

    class NegativeValueError(AlfredPdfToolsError):
        pass

    try:

        if not query.lstrip("+-").isdigit():
            raise NotIntegerError('The argument is not an integer.')

        if int(query) < 0:
            raise NegativeValueError('Negative integer is not a valid argument.')

        page_count = int(query)
        start = 0
        stop = page_count
        inp_file = PdfFileReader(open(abs_path, 'rb'))
        num_pages = int(inp_file.getNumPages())
        quotient = num_pages / page_count

        if quotient.is_integer():

            for i in xrange(int(quotient)):
                merger = PdfFileMerger()
                merger.append(inp_file, pages=(start, stop))
                no_ext_path = os.path.splitext(abs_path)[0]
                merger.write(no_ext_path + (' (part {}).pdf').format(i+1))
                start = stop
                stop = start + page_count

        else:

            for i in xrange(int(quotient) + 1):
                merger = PdfFileMerger()
                merger.append(inp_file, pages=(start, stop))
                no_ext_path = os.path.splitext(abs_path)[0]
                merger.write(no_ext_path + (' (part {}).pdf').format(i+1))
                if i != int(quotient) - 1:
                    start = stop
                    stop = start + page_count
                else:
                    start = int(quotient) * page_count
                    stop = num_pages

    except NotIntegerError as err:
        print err

    except NegativeValueError as err:
        print err

    except ZeroDivisionError:
        print 'Zero is not a valid argument. Enter a positive integer instead.'

if __name__ == '__main__':
    sys.exit(main())
