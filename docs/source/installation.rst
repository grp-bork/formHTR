Installation
============

From PyPI:

.. code-block:: bash

   pip install formhtr

System packages
---------------

- **zbar** — required by ``pyzbar`` (barcode decoding).
- **qpdf** — used for some PDF workflows.
- **Poppler** (``pdfinfo``, etc.) — required by ``pdf2image`` for rasterizing PDFs.

macOS (Homebrew):

.. code-block:: bash

   brew install zbar qpdf poppler

Debian / Ubuntu:

.. code-block:: bash

   sudo apt-get install libzbar0 qpdf poppler-utils

CLI entry point
---------------

.. code-block:: bash

   formhtr --help
