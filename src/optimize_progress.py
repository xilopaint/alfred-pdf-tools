#!/usr/bin/python
# encoding: utf-8

import sys
from workflow import Workflow3, ICON_WARNING


def main(wf):

    page_count = wf.cached_data('page_count', max_age=0)
    page_number = wf.cached_data('page_number', max_age=10)

    wf.rerun = 1

    if not page_number:

        if wf.cached_data_age('page_count') < 10:
            title = "Reading the PDF file..."
            wf.add_item(valid=True, title=title)
        else:
            title = "Optimize action is not running."
            wf.add_item(valid=True, title=title, icon=ICON_WARNING)

    else:

        if page_number != page_count:
            progress = int(round((float(page_number) / float(page_count)) * 100))
            title = "Page {} of {} processed ({}% completed)".format(page_number, page_count, str(progress))
            wf.add_item(valid=True, title=title)

        else:
            progress = int(round((float(page_number) / float(page_count)) * 100))
            title = "Page {} of {} processed ({}% completed)".format(page_number, page_count, str(progress))
            wf.add_item(valid=True, title=title, icon='checkmark.png')

    wf.send_feedback()


if __name__ == '__main__':

    wf = Workflow3()
    sys.exit(wf.run(main))
