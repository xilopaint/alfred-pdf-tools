#!/usr/bin/python
# encoding: utf-8

import sys
import os
from workflow import Workflow3, notify
from subprocess import Popen, PIPE


def main(wf):

    abs_path = os.environ['abs_path']
    query = os.environ['query']
    f = abs_path.split('\t')
    n = len(f)

    class AlfredPdfToolsError(Exception):
        pass

    class NotIntegerError(AlfredPdfToolsError):
        pass

    class NegativeValueError(AlfredPdfToolsError):
        pass

    try:

        if query:
            if not query.lstrip('+-').isdigit():
                raise NotIntegerError

        if query:
            if int(query) < 0:
                raise NegativeValueError

        for i in xrange(n):
            command = "echo -y | ./k2pdfopt '{}' -as -mode copy -dpi {} -o '%s (optimized).pdf' -x".format(f[i], query)
            proc = Popen(command, shell=True, stdout=PIPE)

            while proc.poll() is None:
                line = proc.stdout.readline()
                if "Reading" in line:
                    page_count = line.split()
                    wf.cache_data('page_count', page_count[1])

                if "SOURCE PAGE" in line:
                    page_number = line.split()
                    wf.cache_data('page_number', page_number[2])

            notify.notify('Alfred PDF Tools',
                          'Optimization successfully completed.')

    except NotIntegerError:
        notify.notify('Alfred PDF Tools',
                      'The argument is not an integer.')

    except NegativeValueError:
        notify.notify('Alfred PDF Tools',
                      'Negative integer is not a valid argument.')


if __name__ == '__main__':

    wf = Workflow3()
    sys.exit(wf.run(main))
