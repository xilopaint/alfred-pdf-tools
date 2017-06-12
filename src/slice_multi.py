#!/usr/bin/python
# encoding: utf-8

import sys
import os
from PyPDF2 import PdfFileMerger, PdfFileReader


def main():

    abs_path = os.environ['abs_path']
    query = os.environ['query']
    args = [x.strip() for x in query.split(',')]

    class AlfredPdfToolsError(Exception):
        pass

    class SyntaxError(AlfredPdfToolsError):
        pass

    class IndexError(AlfredPdfToolsError):
        pass

    class StartValueError(AlfredPdfToolsError):
        pass

    try:

        reader = PdfFileReader(open(abs_path, 'rb'))
        page_count = reader.getNumPages()
        arg = [x.split('-') for x in args]

        for n in xrange(len(args)):

            if args[n].replace('-', '').isdigit():
                pass

            else:
                raise SyntaxError('The command syntax is invalid.')

        for n in xrange(len(args)):

            if '-' in args[n]:

                stop = int(arg[n][1])

                if stop > page_count:
                    raise IndexError('Page number out of range.')

                else:
                    pass

            else:

                stop = int(args[n])
                if stop > page_count:
                    raise IndexError('Page number out of range.')

                else:
                    pass

        for n in xrange(len(args)):

            if '-' in args[n]:
                merger = PdfFileMerger()
                reader = PdfFileReader(open(abs_path, 'rb'))
                start = int(arg[n][0]) - 1
                stop = int(arg[n][1])

                if start == -1:
                    raise StartValueError('Page number cannot be zero.')

                if start >= stop:
                    raise StartValueError('You cannot set a page range in reverse order.')

                merger.append(reader, pages=(start, stop))
                no_ext_path = os.path.splitext(abs_path)[0]
                merger.write(no_ext_path + (' (part {}).pdf').format(n + 1))

            else:
                merger = PdfFileMerger()
                reader = PdfFileReader(open(abs_path, 'rb'))
                start = int(args[n]) - 1
                stop = int(args[n])
                merger.append(reader, pages=(start, stop))
                no_ext_path = os.path.splitext(abs_path)[0]
                merger.write(no_ext_path + (' (part {}).pdf').format(n + 1))

    except SyntaxError as err:
        print err

    except IndexError as err:
        print err

    except StartValueError as err:
        print err


if __name__ == '__main__':

    sys.exit(main())
