![alt text](src/icon.png)

# Alfred PDF Tools

A workflow for [Alfred][1].

## Description

Optimize, encrypt and manipulate PDF files.

## Download and Installation

Download the workflow file from [GitHub releases][2] and install it by double-clicking on `Alfred.PDF.Tools.alfredworklow`.

## Usage

**Alfred PDF Tools** can be used by the following file actions:

* `Optimize`: Optimize the selected PDF files by entering the intended resolution of the output file (150 dpi is set once no value is input). The document will be improved on the process with increased contrast and text straightening. Invoke Alfred and type the keyword `progress` if you want to track the optimization process;
* `Encrypt`: Encrypt the selected PDF files by entering a password;
* `Decrypt`: Decrypt the selected PDF files by entering their password or just `↩` if they're not password protected;
* `Merge`: Merge the selected PDF files. Use the `⌘` modifier key if you also want to move the source files to Trash;
* `Split by Page Count`: Split the selected PDF file by page count.
* `Split by File Size`: Split the selected PDF file by file size.
* `Slice in Multiple Files`: Slice the selected PDF file in multiple files by entering page numbers and/or page ranges separated by commas (e.g. 2, 5-8, 20-).
* `Slice in a Single File`: Slice the selected PDF file in a single file by entering page numbers and/or page ranges separated by commas (e.g. 2, 5-8, 20-).
* `Crop`: Convert two-column pages in single pages.
* `Scale`: Scale the selected PDF files to a given paper size.

## Contribute

To report a bug or request a feature, please [create an issue][3] or [submit a pull request][4].

## Credits

This workflow relies on [pikepdf][5] library by James R. Barlow, [docopt][6] by  Vladimir Keleshev, [K2pdfopt][7] by Johannes Buchnerand and [Send2Trash][8] by Virgil Dupras.

## License

**Alfred PDF Tools** is released under the [MIT License][9].

[1]:http://www.alfredapp.com/
[2]:https://github.com/xilopaint/alfred-pdf-tools/releases/latest
[3]:https://github.com/xilopaint/alfred-pdf-tools/issues
[4]:https://github.com/xilopaint/alfred-pdf-tools/pulls
[5]:https://github.com/pikepdf/pikepdf
[6]:https://github.com/docopt/docopt
[7]:http://www.willus.com/k2pdfopt/
[8]:https://github.com/hsoft/send2trash
[9]:https://opensource.org/licenses/MIT
