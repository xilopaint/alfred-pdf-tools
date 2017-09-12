#!/usr/bin/python
# encoding: utf-8

import sys
import os
from workflow import Workflow3, notify
import ntpath
from PyPDF2 import PdfFileMerger, PdfFileReader
from send2trash import send2trash


def main(wf):

    abs_paths = os.environ['abs_paths']
    query = os.environ['query']
    files = abs_paths.split('\t')
    paths = [get_path(path) for path in files]
    merger = PdfFileMerger(strict=False)

    class AlfredPdfToolsError(Exception):
        pass

    class SelectionError(AlfredPdfToolsError):
        pass

    class MultiplePathsError(AlfredPdfToolsError):
        pass

    try:

        if len(files) < 2:
            raise SelectionError

        if not check_equal(paths):
            raise MultiplePathsError

        for pdf in files:
            reader = PdfFileReader(open(pdf, 'rb'))
            merger.append(reader)

        for pdf in files:
            send2trash(pdf)

        merger.write(paths[0] + "/" + query + ".pdf")

    except SelectionError:
        notify.notify('Alfred PDF Tools',
                      'You must select at least two PDF files to merge.')

    except MultiplePathsError:
        notify.notify('Alfred PDF Tools',
                      'Cannot merge PDF files from multiple paths.')


def check_equal(paths):

    return paths[1:] == paths[:-1]


def get_path(path):

    head, tail = ntpath.split(path)
    return head


if __name__ == '__main__':

    wf = Workflow3()
    sys.exit(wf.run(main))
