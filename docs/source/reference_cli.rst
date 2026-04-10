Command-line interface
======================

The ``formhtr`` console script invokes :func:`formhtr.cli.main`. The parser below is the
single source of truth for flags and subcommands (see :mod:`formhtr.cli`).

.. argparse::
   :module: formhtr.cli
   :func: _build_parser
   :prog: formhtr

.. automodule:: formhtr.cli
   :members:
   :exclude-members: _build_parser
