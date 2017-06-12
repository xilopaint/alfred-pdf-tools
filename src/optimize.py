#!/usr/bin/python
# encoding: utf-8

import sys
import os
from subprocess import call, STDOUT


def main():

    abs_path = os.environ['abs_path']
    query = os.environ['query']
    files = abs_path.split('\t')
    n = len(files)

    class AlfredPdfToolsError(Exception):
        pass

    class NotIntegerError(AlfredPdfToolsError):
        pass

    class NegativeValueError(AlfredPdfToolsError):
        pass

    try:

        if query:
            if not query.lstrip("+-").isdigit():
                raise NotIntegerError('The argument is not an integer.')

        if query:
            if int(query) < 0:
                raise NegativeValueError('Negative integer is not a valid argument.')

        for i in xrange(n):
            bash_cmd("echo -y | ./k2pdfopt -as -mode copy -dpi {} -o '%s (optimized).pdf' -x '{}'".format(query, files[i]))

        print "Optimization successfully completed."

    except NotIntegerError as err:
        print err

    except NegativeValueError as err:
        print err


def bash_cmd(command):

    fnull = open(os.devnull, 'w')
    call(command, shell=True, executable="/bin/bash", stdout=fnull, stderr=STDOUT)


if __name__ == "__main__":

    sys.exit(main())
