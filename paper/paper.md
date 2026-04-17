---
title: 'formHTR: A Python package for handprint text recognition in form documents'
tags:
  - Python
  - OCR
authors:
  - name: Matej Troják
    orcid: 0000-0003-0841-2707
    corresponding: true
    affiliation: 1
  - name: Jan Glos
    affiliation: 3
  - name: Stéphane Pesant
    orcid: 0000-0002-4936-5209
    affiliation: 2
  - name: Peer Bork
    orcid: 0000-0002-2627-833X
    affiliation: 1
affiliations:
 - name: EMBL, Heidelberg, Germany
   index: 1
   ror: "03mstc592"
 - name: EMBL-EBI, Hinxton, UK
   index: 2
   ror: "02catss52"
 - name: Masaryk university, Czech republic
   index: 3
   ror: "02j46qs45"
date: 14 April 2026
bibliography: paper.bib
---

# Summary

The formHTR is a Python software package for automatic extraction of (handwritten) contents from scanned PDF form documents. While extraction step itself is secured using advanced OCR models, a key step in the process is annotation of the regions of interest in the form. This significantly improves the success rate of the outputs by providing expected content locations and types. The identified contents using the OCR models can be then compared and evaluated using such a specification.

# Statement of need

Large-scale scientific expeditions often collect huge amounts of samples, with a need to write down the context of the samples and observed features. While digital forms are getting more popular, paper forms are still the mostly used form for their reliability in extreme environments, stability, and ease to use [@VANTAMELEN2004123,@BREWER2016131]. 

- need of automatic processing using multiple OCR models allowing decision making
- target audience is primarily non-technical
- fusion of results with inputs

Additionally, assuming a large-scale expedition enforces certain standards on the sample collection process, so does on the metadata level. That means standardised forms are often developed, and used over and over in various sampling scenarious. As a consequence, to digitalise the contents of such forms, we can leverage the known structure and expected content types of such documents, and navigate the OCR methods for more reliable results.

# State of the field

There are several large OCR models provided by major IT companies - these include Google Cloud Vision API [@google_vision_api], Azure AI Document Intelligence [@azure_form_recognizer] and Amazon Textract [@amazon_textract]. There are also smaller libraries such as Tesseract OCR Engine [@tesseract_ocr] or OCR4all [@ocr4all], as well as tool handprint combining them [@handprint].

- handprint combining it, but not maintained anymore, + does not allow the annotation

# Software design

![Schematic overview of formHTR annotation and processing workflow. \label{fig:scheme}](scheme.png)

- highlight voting algorithm, explain future improvements?
- explain rtree [@rtree] approach overlaps

# Research impact statement

TODO

- used in TREC expediiton for extraction of metadata[^1] from more than 10k logsheet forms

[^1]: https://www.ebi.ac.uk/biosamples/samples?text=Traversing+European+Coastlines+%28TREC%29+expedition

# Example workflow

TODO

# Author's Contributions

TODO

# AI usage disclosure

No generative AI tools were used in the development of this software, the writing
of this manuscript, or the preparation of supporting materials.

# Acknowledgements

- TREC project / EMBL internal 

# References