#!/usr/bin/python
# encoding: utf-8

import sys
import os
from PyPDF2 import PdfFileReader, PdfFileWriter

def main():

    abs_path = os.environ['abs_path']
    query = os.environ['query']
    no_ext_path = os.path.splitext(abs_path)[0]

    try:

        inp_file = open(abs_path, 'rb')
        pdf_reader = PdfFileReader(inp_file, strict=False)
        pdf_writer = PdfFileWriter()

        for pageNum in range(pdf_reader.numPages):
            pdf_writer.addPage(pdf_reader.getPage(pageNum))

        pdf_writer.encrypt(query)
        out_file = open(no_ext_path + ' (encrypted).pdf', 'wb')
        pdf_writer.write(out_file)
        out_file.close()

    except Exception as err:
        print err

if __name__ == '__main__':

    sys.exit(main())
