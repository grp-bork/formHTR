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
- infeaseble to train models on multiple ever changing set of handwritings

Additionally, assuming a large-scale expedition enforces certain standards on the sample collection process, so does on the metadata level. That means standardised forms are often developed, and used over and over in various sampling scenarious. As a consequence, to digitalise the contents of such forms, we can leverage the known structure and expected content types of such documents, and navigate the OCR methods for more reliable results.

# State of the field

There are several large OCR models provided by major IT companies - these include Google Cloud Vision API [@google_vision_api], Azure AI Document Intelligence [@azure_form_recognizer] and Amazon Textract [@amazon_textract]. There are also smaller libraries such as Tesseract OCR Engine [@tesseract_ocr] or OCR4all [@ocr4all], as well as tool handprint combining them [@handprint].

- handprint combining it, but not maintained anymore, + does not allow the annotation

# Software design

The tool is structured into two main parts. The first part, further devided into two substeps, is dedicated to annotating form document templates in order to specify the regions of interest (ROIs) and assign them a meaning (variable name and type). The first substep is used solely for selecting the regions and manipulating their position, while the second substep inserts variable names and types into individual ROIs. The output of the whole step is a config file containing position, name, and type of identified ROIs.

![Schematic overview of formHTR annotation and processing workflow. \label{fig:scheme}](scheme.png)

The second step identifies and extracts content from the ROIs. The first substep is to align the scanned document with its template. The motivation of this step is to ensure the ROIs actually match the regions in the scannned document, otherwise they would point to potentially empty or generally nonsense regions. While the task is rather straightforward, the execution can be tricky especially when the template has no fiducial markers or the scan quality is low. For this reason, a manual alignment is possible as well.

The second substep is to convert the aligned document to an image and query several OCR models to identify and extract the content. For this purpose, three services are used by calling their respective APIs - Google Cloud Vision [@google_vision_api], Azure AI Document Intelligence [@azure_form_recognizer], and Amazon Textract [@amazon_textract]. All three services output a list of extracted content with its location (bounding box) in the image.[^1]

[^1]: All services offer a free tier with limited amount of requests per month, but the user needs to register and obtain access credentials. We try to keep the steps how to do it up-to-date on the [wiki pages](link_TODO) of the repository, but it's a highly variable process beyond our control.

Next step is a binning of identified contents into the ROIs for each service. A corresponding ROI needs to be decided for each captured fragment of text (a word). There are several cases that need to be considered, such as a word spanning over multiple ROIs or multiple words overlapping with a single ROI. To find all overlaps for a ROI from all the services, the number of possibilities and cases that need to be investigated can grow. We use ```rtree``` [@rtree] to index the regions and capture their overlaps for all services and the template specification, consequently allowing an effective querying for matches. Additionally, the document can contain preprinted contents (residuals) that do not belong to ROIs, but an imperfect alignment can shift them into a ROI. This is handled by defining the residuals already in the annotation step, allowing their elimination from the outputs. 

Assuming the words are binned for all services, we can use a voting algorithm to pick the most likely output. With three services, we can use a majority vote. In cases when there is no concensus, a random choice is made. Similarly, the tool works even with one or two services enabled, but naturally the quality of the output is lower because the voting cannot be effectively used. On top of voting, the weight of votes can be altered by using the known information about the ROIs. In the current version, priority to numerical values (if expected) is given. This aspect has a very high potential for extensions in the future versions (e.g. allow only values from a dictionary, limit the length of content, satisfy a regex, number in an integer range).

Finally, the output of the tool is an Excel spreadsheet (an ```.xlsx``` file) with two sheets. The first sheet has three columns - variable name coming from the specification, extracted content as the result coming from the voting algorithm, and insterted picture cut out of the scanned (and aligned) document in the bouding box defined in the specification. This can be used for quick proofreading of the outputs. The second sheet contains any miscellaneous content that did not fall into any ROI nor was flagged as a residual. This can typically alert the user to any comments and notes written in unexpected parts of the document.

# Research impact statement

TODO

- used in TREC expediiton for extraction of metadata[^2] from more than 10k logsheet forms

[^2]: https://www.ebi.ac.uk/biosamples/samples?text=Traversing+European+Coastlines+%28TREC%29+expedition

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