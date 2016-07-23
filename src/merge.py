#!/usr/bin/env python
# encoding: utf-8

import sys
from PyPDF2 import PdfFileMerger, PdfFileReader
from send2trash import send2trash
from os.path import expanduser
import ntpath


def main():

    query = sys.argv[1:]
    files = [x for x in query if x.endswith('.pdf')]
    paths = [get_path(path) for path in files]
    merger = PdfFileMerger()

    class AlfredPdfSuiteError(Exception):
        pass

    class SelectionError(AlfredPdfSuiteError):
        pass

    class MultiplePathsError(AlfredPdfSuiteError):
        pass

    try:

        if len(files) < 2:
            raise SelectionError('You must select at least two PDF files to merge.')

        if not check_equal(paths):
            raise MultiplePathsError('Cannot merge PDF files from multiple paths.')

        for pdf in files:
            merger.append(PdfFileReader(open(pdf, 'rb')))

        merger.write(paths[0] + "/output.pdf")

        for pdf in files:
            send2trash(pdf)

    except SelectionError as err:
        print err

    except MultiplePathsError as err:
        print err


def check_equal(paths):

   return paths[1:] == paths[:-1]


def get_path(path):

    head, tail = ntpath.split(path)
    return head


if __name__ == "__main__":
    sys.exit(main())
