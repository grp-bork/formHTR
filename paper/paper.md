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

TODO

# Statement of need

TODO

- need of automatic processing using multiple OCR models allowing decision making
- target audience is primarily non-technical
- motivated by large-scale expedition, high abundance of instances of the same forms, following the need to annotate the template to increase the content extraction chances
- fusion of results with inputs

# State of the field                                                                                                                  

- individual OCR setvices and packages
- handprint combining it, but not maintained anymore, + does not allow the annotation

# Software design

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