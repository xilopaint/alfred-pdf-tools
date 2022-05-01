<h1 align="center">Alfred PDF Tools</h1>

<p align="center">
  <a href="https://github.com/xilopaint/alfred-pdf-tools/releases/latest">
  <img src="https://img.shields.io/github/v/release/xilopaint/alfred-pdf-tools"></a>
  <a href="https://github.com/xilopaint/alfred-pdf-tools/releases">
  <img src="https://img.shields.io/github/downloads/xilopaint/alfred-pdf-tools/total"></a>
  <a href="https://www.codacy.com/gh/xilopaint/alfred-pdf-tools/dashboard">
  <img src="https://app.codacy.com/project/badge/Grade/3b9d7ae47ec34509a2ba833b0e0d5cc0"></a>
  <a href="https://github.com/PyCQA/bandit">
  <img src="https://img.shields.io/badge/security-bandit-yellow"></a>
  <a href="https://github.com/xilopaint/alfred-pdf-tools/blob/main/LICENSE.md">
  <img src="https://img.shields.io/github/license/xilopaint/alfred-pdf-tools"></a>
</p>

<p align="center">
  <img src="src/icon.png">
</p>

## Description

Optimize, encrypt and manipulate PDF files using [Alfred][1].

## Usage

**Alfred PDF Tools** can be used by the following [file actions][2]:

* `Optimize`: Optimize the selected PDF files by entering the intended
  resolution of the output file (150 dpi is used if no value is input) and the
  document will be improved with increased contrast and straightened text;
* `Deskew`: Straighten the selected PDF files with no further appearance changes;

> Tip: Invoke Alfred and type the `progress` keyword to track the enhancement
> process from either of the first two mentioned file actions.

* `Encrypt`: Encrypt the selected PDF files by entering a password;
* `Decrypt`: Decrypt the selected PDF files by entering their password or just
  `↩` if they're not password protected;
* `Merge`: Merge the selected PDF files. Use the `⌘` modifier key if you also
  want to move the source files to Trash;
* `Split by Page Count`: Split the selected PDF file by page count;
* `Split by File Size`: Split the selected PDF file by file size;
* `Slice in Multiple Files`: Slice the selected PDF file in multiple files by
   entering page numbers and/or page ranges separated by commas (e.g. 2, 5-8, 20-);
* `Slice in a Single File`: Slice the selected PDF file in a single file by
  entering page numbers and/or page ranges separated by commas (e.g. 2, 5-8, 20-);
* `Crop`: Convert two-column pages in single pages;
* `Scale`: Scale the selected PDF files to a given paper size.

## Contribute

To report a bug or request a feature, please [create an issue][3] or [submit a
pull request][4].

## Credits

This workflow relies on [pikepdf][5] library by James R. Barlow, [docopt][6] by
Vladimir Keleshev, [K2pdfopt][7] by Johannes Buchnerand and [Send2Trash][8] by
Virgil Dupras.

[1]:http://www.alfredapp.com/
[2]:https://www.alfredapp.com/blog/tips-and-tricks/file-actions-from-alfred-or-finder/
[3]:https://github.com/xilopaint/alfred-pdf-tools/issues
[4]:https://github.com/xilopaint/alfred-pdf-tools/pulls
[5]:https://github.com/pikepdf/pikepdf
[6]:https://github.com/docopt/docopt
[7]:http://www.willus.com/k2pdfopt/
[8]:https://github.com/hsoft/send2trash
