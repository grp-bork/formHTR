Reference
=========

Navigation for the command-line interface, the main Python entry points, and the
internal ``formhtr.libs`` packages they build on.

CLI
---

* :doc:`reference_cli` — All ``formhtr`` subcommands and options (generated from :mod:`argparse`).

Core API
--------

* :doc:`reference_api_core` — Logsheet OCR pipeline (:func:`~formhtr.logsheet.extract_logsheet`,
  :func:`~formhtr.logsheet.process_logsheet_to_xlsx`, helpers) and interactive ROI helpers
  (:mod:`formhtr.roi_tools`).

  * ``extract_logsheet`` / preprocessing draws on :doc:`reference_libs_processing`,
    :doc:`reference_libs_services`, and :doc:`reference_libs_support`.
  * ``select_rois`` / ``annotate_rois`` draw on :doc:`reference_libs_extract` and
    :doc:`reference_libs_annotate`.

Other API modules
-----------------

* :doc:`reference_api_other` — Export-only pipeline, alignment helpers, PDF sizing, and
  system dependency checks (:mod:`formhtr.export_logsheet`, :mod:`formhtr.auto_align`,
  :mod:`formhtr.manual_align`, :mod:`formhtr.pdf_utils`, :mod:`formhtr.deps`).

Library internals (``formhtr.libs``)
------------------------------------

* :doc:`reference_libs_extract` — Rectangle detection, ROI selection CLI bridge, selection UI
  (:mod:`formhtr.libs.extract_ROI`).
* :doc:`reference_libs_annotate` — ROI labelling UI and helpers (:mod:`formhtr.libs.annotate_ROI`).
* :doc:`reference_libs_processing` — Alignment, checkbox/barcode handling, content parsing,
  spatial indexing, spreadsheet output (:mod:`formhtr.libs.processing`).
* :doc:`reference_libs_services` — Google / Amazon / Azure Vision adapters and orchestration
  (:mod:`formhtr.libs.services`).
* :doc:`reference_libs_support` — PDF rasterization, layout config, geometry types, statistics,
  debug visualisation (:mod:`formhtr.libs` top-level modules).

.. toctree::
   :maxdepth: 1
   :caption: Reference pages

   reference_cli
   reference_api_core
   reference_api_other
   reference_libs_extract
   reference_libs_annotate
   reference_libs_processing
   reference_libs_services
   reference_libs_support
