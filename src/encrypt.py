#!/usr/bin/python
# encoding: utf-8

import sys
import os
from PyPDF2 import PdfFileReader, PdfFileWriter

def main():

    abs_path = os.environ['abs_path']
    query = os.environ['query']
    files = abs_path.split('\t')
    no_ext_path = [os.path.splitext(x) for x in files]
    file_count = len(files)

    for n in xrange (file_count):

        inp_file = open(files[n], 'rb')
        pdf_reader = PdfFileReader(inp_file, strict=False)
        pdf_writer = PdfFileWriter()

        for pageNum in range(pdf_reader.numPages):
            pdf_writer.addPage(pdf_reader.getPage(pageNum))

        pdf_writer.encrypt(query)
        out_file = open(no_ext_path[n][0] + ' (encrypted).pdf', 'wb')
        pdf_writer.write(out_file)
        out_file.close()

if __name__ == '__main__':

    sys.exit(main())
