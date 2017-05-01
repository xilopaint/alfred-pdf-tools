#!/usr/bin/python
# encoding: utf-8

import sys
import os
import ntpath
from PyPDF2 import PdfFileMerger, PdfFileReader
from send2trash import send2trash

def main():

    abs_paths = os.environ['abs_paths']
    query = os.environ['query']
    files = abs_paths.split('\t')
    paths = [get_path(path) for path in files]
    merger = PdfFileMerger(strict = False)

    class AlfredPdfToolsError(Exception):
        pass

    class SelectionError(AlfredPdfToolsError):
        pass

    class MultiplePathsError(AlfredPdfToolsError):
        pass

    try:

        if len(files) < 2:
            raise SelectionError('You must select at least two PDF files to merge.')

        if not check_equal(paths):
            raise MultiplePathsError('Cannot merge PDF files from multiple paths.')

        for pdf in files:
            reader = PdfFileReader(open(pdf, 'rb'))
            merger.append(reader)

        for pdf in files:
            send2trash(pdf)

        merger.write(paths[0] + "/" + query + ".pdf")

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
