#!/usr/bin/python
# encoding: utf-8

from __future__ import division
import sys
import os
from workflow import Workflow3, notify
from PyPDF2 import PdfFileMerger, PdfFileReader


def main(wf):

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
                no_ext_path = os.path.splitext(abs_path)[0]
                merger.write(no_ext_path + (' (part {}).pdf').format(i + 1))
                start = stop
                stop = start + page_count

        else:

            for i in xrange(int(quotient) + 1):
                merger = PdfFileMerger(strict=False)
                merger.append(inp_file, pages=(start, stop))
                no_ext_path = os.path.splitext(abs_path)[0]
                merger.write(no_ext_path + (' (part {}).pdf').format(i + 1))
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
        print 'Zero is not a valid argument. Enter a positive integer instead.'


if __name__ == '__main__':

    wf = Workflow3()
    sys.exit(wf.run(main))
