Core API
========

Logsheet pipeline
-----------------

The main OCR path rasterizes and aligns the scan, calls cloud vision services, and parses
ROIs. Start with :func:`~formhtr.logsheet.extract_logsheet` for in-process use, or
:func:`~formhtr.logsheet.process_logsheet_to_xlsx` to write a workbook.

.. automodule:: formhtr.logsheet
   :members:
   :member-order: bysource

ROI tools
---------

Interactive definition and labelling of regions on a template PDF. These wrap the widgets
and helpers under :doc:`reference_libs_extract` and :doc:`reference_libs_annotate`.

.. automodule:: formhtr.roi_tools
   :members:
   :member-order: bysource
