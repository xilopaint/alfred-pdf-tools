#!/usr/bin/python
# encoding: utf-8

import sys
import os
from workflow import Workflow3, notify
from PyPDF2 import PdfFileMerger, PdfFileReader


def main(wf):

    abs_path = os.environ['abs_path']
    query = os.environ['query']
    args = [x.strip() for x in query.split(',')]

    class AlfredPdfToolsError(Exception):
        pass

    class SyntaxError(AlfredPdfToolsError):
        pass

    class IndexError(AlfredPdfToolsError):
        pass

    class StartValueZeroError(AlfredPdfToolsError):
        pass

    class StartValueReverseError(AlfredPdfToolsError):
        pass

    try:

        reader = PdfFileReader(open(abs_path, 'rb'))
        merger = PdfFileMerger(strict=False)
        page_count = reader.getNumPages()
        arg = [x.split('-') for x in args]

        for n in xrange(len(args)):

            if args[n].replace('-', '').isdigit():
                pass

            else:
                raise SyntaxError

        for n in xrange(len(args)):

            if '-' in args[n]:

                stop = int(arg[n][1])

                if stop > page_count:
                    raise IndexError

                else:
                    pass

            else:

                stop = int(args[n])
                if stop > page_count:
                    raise IndexError

                else:
                    pass

        for n in xrange(len(args)):

            if '-' in args[n]:

                start = int(arg[n][0]) - 1
                stop = int(arg[n][1])

                if start == -1:
                    raise StartValueZeroError

                if start >= stop:
                    raise StartValueReverseError

                merger.append(reader, pages=(start, stop))

            else:

                start = int(args[n]) - 1
                stop = int(args[n])
                merger.append(reader, pages=(start, stop))

        no_ext_path = os.path.splitext(abs_path)[0]
        merger.write(no_ext_path + ' (slice).pdf')

    except SyntaxError:
        notify.notify('Alfred PDF Tools', 'The command syntax is invalid.')

    except IndexError:
        notify.notify('Alfred PDF Tools', 'Page number out of range.')

    except StartValueZeroError:
        notify.notify('Alfred PDF Tools', 'Page number cannot be zero.')

    except StartValueReverseError:
        notify.notify('Alfred PDF Tools',
                      'You cannot set a page range in reverse order.')


if __name__ == '__main__':

    wf = Workflow3()
    sys.exit(wf.run(main))
