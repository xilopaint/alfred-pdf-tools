# Alfred PDF Tools

A workflow for [Alfred 3][1].  

## Description

Optimize, encrypt and manipulate PDF files.

## Download and Installation

Download the workflow file either from [GitHub releases][2] and install it by double-clicking on `Alfred PDF Tools.alfredworklow`.

## Usage

**Alfred PDF Tools** can be used by the following file actions:

* `Optimize`: Compress and optimize the selected PDF files by entering the intended resolution of the output file (150 dpi is set once no value is input). The document will be improved on the process with increased contrast and text straightening;
* `Encrypt`: Encrypt the selected PDF file by entering a password;
* `Merge`: Merge the selected PDF files and move the source files to trash;
* `Split by Page Count`: Split the selected PDF file by entering the maximum amount of pages for each new PDF file;
* `Split by File Size`: Split the selected PDF file by entering the maximum file size in MB for each new PDF file;
* `Slice`:  Slice the selected PDF file by entering start, stop and step arguments separated by commas (e.g., "10, 20, 1" will create a PDF file from pages 10 to 20 of the source file).

## Contribute

To report a bug or submit a feature request, please [create an issue][3] or [submit a pull request][4] on GitHub.

## Credits

This workflow relies on [PyPDF2][5] library currently maintained by [Phaseit, Inc.][6], [K2pdfopt][7] by Johannes Buchnerand, [Send2Trash][8] by Virgil Dupras and [OneUpdater][9] by Vítor Galvão.

## License

**Alfred PDF Tools** code is released under the [MIT License][10].

[1]:http://www.alfredapp.com/
[2]:https://github.com/xilopaint/alfred-pdf-tools/releases/latest
[3]:https://github.com/xilopaint/alfred-pdf-tools/issues
[4]:https://github.com/xilopaint/alfred-pdf-tools/pulls
[5]:https://github.com/mstamy2/PyPDF2
[6]:http://phaseit.net
[7]:http://www.willus.com/k2pdfopt/
[8]:https://github.com/hsoft/send2trash
[9]:https://github.com/vitorgalvao/alfred-workflows/tree/master/OneUpdater
[10]:https://opensource.org/licenses/MIT