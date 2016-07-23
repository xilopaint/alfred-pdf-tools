#!/usr/bin/env python
# encoding: utf-8

import sys
from PyPDF2 import PdfFileMerger, PdfFileReader
import os.path


def main():

    abs_path = os.environ['abs_path']
    query = os.environ['query']
    args = [x.strip() for x in query.split(',')]
    start = int(args[0])-1
    stop = int(args[1])
    step = int(args[2])
    merger = PdfFileMerger()
    inp_file = PdfFileReader(open(abs_path, 'rb'))

    class AlfredPdfSuiteError(Exception):
        pass

    class StartValueError(AlfredPdfSuiteError):
        pass

    class StepValueError(ValueError):
        pass

    try:

        if not abs_path:
            raise NoFileError('You must select a PDF file.')

        if start <= -1:
            raise StartValueError('Start argument cannot be zero or negative value.')

        if start >= stop:
            raise StartValueError('Start argument cannot be greater than stop argument.')

        if step <= 0:
            raise StepValueError('Step argument cannot be zero or negative value.')

        merger.append(inp_file, pages=(start, stop, step))
        par_path = os.path.abspath(os.path.join(abs_path, os.pardir))
        merger.write(par_path + '/output.pdf')

    except StartValueError as err:
        print err

    except StepValueError as err:
        print err

    except IndexError:
        print 'Stop value out of range'

if __name__ == '__main__':
    sys.exit(main())

