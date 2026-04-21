---
title: 'formHTR: A Python package for handwritten text recognition in form documents'
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

The formHTR is a Python software package for automatic extraction of handwritten contents from scanned form documents. While extraction step itself is secured using advanced pretrained OCR models, a key step in the process is considering the prior knowledge of the expected contents. That is achieved by the precise, semi-automatic annotation of the regions of interest (ROIs) in the form template, specifying the locations and content types of ROIs. Using this approach in combination with comparing and evaluating outputs from multiple OCR models significantly improves the quality of the extraction.

# Statement of need

Large-scale scientific expeditions often collect huge amounts of samples, with a need to write down the context of the samples and observed features (metadata). While digital metadata collection methods are getting more popular, paper forms (so called *logsheets*) are still the most popular method for their reliability in extreme environments, stability, natural scalability, and ease to use ([@VANTAMELEN2004123], [@BREWER2016131]).

It is neccesary build an infrastructure for processing of the logsheets automatically with minimum of manual interventions and laborious proofreading. Optical character recognition (OCR) methods [@ocr156468] are used to extract the content from a scanned logsheet, with additional complexity added by handwritten type of content. While training custom models on a particular handwritting style of a person is generally more precise, in a large-scale expeditions, the turnaround of staff and consequently the amount of distict handwrittings is usually infeasible. The use of multiple pretrained general purpose OCR models, allowing consensus or majority decision making, is a more suitable approach.

Additionally, assuming a large-scale expedition enforces certain standards on the sample collection process, so does on the metadata level. That means standardised logsheets are often developed, and used repeatedly in various sampling scenarious. As a consequence, to digitalise the contents of such logsheets, we can leverage their known structure and expected content types, and navigate the OCR methods for more reliable and precise results.

# State of the field

The current OCR landscape of pretrained tools can be split between open-source models and cloud-based services. On the open-source side, there are many tools such as Tesseract OCR [@tesseract_ocr], EasyOCR [@easyocr], OCR4All [@app9224853], and PaddleOCR [@cui2025paddleocr30technicalreport] provide pretrained models or optionally allow to train custom models. Some of the trade-offs are in accuracy, speed, and deployment complexity. The cloud-based pretrained OCR services, including Google Cloud Vision API [@google_vision_api], Azure AI Document Intelligence [@azure_form_recognizer], and Amazon Textract [@amazon_textract], are accessible via APIs and provide are highly optimized for structured documents and provide higher-level outputs (e.g. key–value pairs).

A natural extension are tools that combine multiple tools, models, or services. Systems such as OCRmyPDF [@ocrmypdf] or unified interfaces like OcrPy [@ocrpy] integrate engines like Tesseract, cloud APIs, and downstream processing into a single pipeline, effectively abstracting over multiple OCR backends. Tool Handprint [@handprint] combines multiple cloud services and outputs annotated images or raw results, as well as compares the recognized text to some level of the ground truth (expected content)[^1].

[^1]: The package is not maintained anymore.

# Software design

The tool is structured into two main parts. The first part, further devided into two substeps, is dedicated to annotating form document templates in order to specify the regions of interest (ROIs) and assign them a meaning (variable name and type). The first substep is used solely for selecting the regions and manipulating their position, while the second substep inserts variable names and types into individual ROIs. The output of the whole step is a config file containing position, name, and type of identified ROIs.

![Schematic overview of formHTR annotation and processing workflow. \label{fig:scheme}](scheme.png)

The second step identifies and extracts content from the ROIs. The first substep is to align the scanned document with its template. The motivation of this step is to ensure the ROIs actually match the regions in the scannned document, otherwise they would point to potentially empty or generally nonsense regions. While the task is rather straightforward, the execution can be tricky especially when the template has no fiducial markers or the scan quality is low. For this reason, a manual alignment is possible as well.

The second substep is to convert the aligned document to an image and query several OCR models to identify and extract the content. For this purpose, three services are used by calling their respective APIs - Google Cloud Vision [@google_vision_api], Azure AI Document Intelligence [@azure_form_recognizer], and Amazon Textract [@amazon_textract]. All three services output a list of extracted content with its location (bounding box) in the image.[^2]

[^2]: All services offer a free tier with limited amount of requests per month, but the user needs to register and obtain access credentials. We try to keep the steps how to do it up-to-date on the [wiki pages](https://github.com/grp-bork/formHTR/wiki/Setup-services) of the repository, but it's a highly variable process beyond our control.

Next step is a binning of identified contents into the ROIs for each service. A corresponding ROI needs to be decided for each captured fragment of text (a word). There are several cases that need to be considered, such as a word spanning over multiple ROIs or multiple words overlapping with a single ROI. To find all overlaps for a ROI from all the services, the number of possibilities and cases that need to be investigated can grow. We use ```rtree``` [@rtree] to index the regions and capture their overlaps for all services and the template specification, consequently allowing an effective querying for matches. Additionally, the document can contain preprinted contents (residuals) that do not belong to ROIs, but an imperfect alignment can shift them into a ROI. This is handled by defining the residuals already in the annotation step, allowing their elimination from the outputs. 

Assuming the words are binned for all services, we can use a voting algorithm to pick the most likely output. With three services, we can use a majority vote. In cases when there is no concensus, a random choice is made. Similarly, the tool works even with one or two services enabled, but naturally the quality of the output is lower because the voting cannot be effectively used. On top of voting, the weight of votes can be altered by using the known information about the ROIs. In the current version, priority to numerical values (if expected) is given. This aspect has a very high potential for extensions in the future versions (e.g. allow only values from a dictionary, limit the length of content, satisfy a regex, number in an integer range).

Finally, the output of the tool is an Excel spreadsheet (an ```.xlsx``` file) with two sheets. The first sheet has three columns - variable name coming from the specification, extracted content as the result coming from the voting algorithm, and insterted picture cut out of the scanned (and aligned) document in the bouding box defined in the specification. This can be used for quick proofreading of the outputs. The second sheet contains any miscellaneous content that did not fall into any ROI nor was flagged as a residual. This can typically alert the user to any comments and notes written in unexpected parts of the document.

# Research impact statement

The tool was used on a set of scanned logsheets containing provenance metadata coming from the Traversing European Coastlines (TREC) expedition[^3]. Roughly 10 thousands double-sided logsheets of roughly 100 different types were collected, together providing contextual metadata to more than 80 thousands collected samples. Using this package, the used logsheet templates were annotated and all the scanned documents processed. The metadata was extracted and curated, and archived[^4] in the BioSamples database [@courtot2022biosamples]. The contextual metadata is an essential base for the samples analysis and data production, which is in initial phase during writing of this manuscript.

[^3]: https://www.embl.org/about/info/trec/

[^4]: https://www.ebi.ac.uk/biosamples/samples?text=Traversing+European+Coastlines+%28TREC%29+expedition

# Example workflow

An example workflow comprises of the three steps, assuming we have a template and scan documents. We first need to create and annotate ROIs for the template, and consequently process it creating the output Excel spreadsheet.

```
# 1) Create ROI config for a template
formhtr select-rois --pdf-file template.pdf --output-file config.json

# 2) Annotate ROI types and variable names
formhtr annotate-rois --pdf-file template.pdf --config-file config.json --output-file config_annotated.json

# 3) Process a scanned logsheet
formhtr process-logsheet \
  --pdf-logsheet scan.pdf \
  --pdf-template template.pdf \
  --config-file config_annotated.json \
  --output-file output.xlsx \
  --google google_credentials.json \
  --amazon amazon_credentials.json \
  --azure azure_credentials.json
```

# Author's Contributions

MT wrote the manuscript and developed the software. JG contributed to the software. SP contributed via conceptual guidance and contributed to the manuscript. PB provided conceptual oversight and funding.

# AI usage disclosure

No generative AI tools were used in the development of this software, or the writing of this manuscript. AI tools were used the preparation of supporting materials, namely setting up and generating the documentation and tests.

# Acknowledgements

This publication was enabled by the support of EMBL member states to the TREC expedition, within the framework of EMBL’s Molecules to Ecosystems Programme (2022-2026).

# References