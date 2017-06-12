# Alfred PDF Tools

A workflow for [Alfred 3][1].  

## Description

Optimize, encrypt and manipulate PDF files.

## Download and Installation

Download the workflow file from [GitHub releases][2] and install it by double-clicking on `Alfred PDF Tools.alfredworklow`.

## Usage

**Alfred PDF Tools** can be used by the following file actions:

* `Optimize`: Optimize the selected PDF files by entering the intended resolution of the output file (150 dpi is set once no value is input). The document will be improved on the process with increased contrast and text straightening;
* `Encrypt`: Encrypt the selected PDF files by entering a password;
* `Merge`: Merge the selected PDF files. Use the `⌘` modifier key if you also want to move the source files to Trash;
* `Split`: Split the selected PDF file either by page count or file size (use the `⌘` modifier key in the latter case);
* `Slice`:  Slice the selected PDF file in multiple files by entering page numbers and/or page ranges separated by commas (e.g. 2, 5-8). For a single file/slice use the `⌘` modifier key.

## Contribute

To report a bug or request a feature, please [create an issue][3] or [submit a pull request][4] on GitHub.

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