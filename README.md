# formHCR
Handprint character recognition in form documents.


# Installation

```
conda env create -f conda_env.yaml
```

# Usage

## Create ROIs

This functionality is split (for now) into two separate scripts.

### select ROIs

Script `select_ROIs.py` is used to find and define locations of regions of interest (ROIs) in the given PDF.

Generally, it is possible to draw ROIs (rectangles) manually but also to detect them automatically.
The coordinates of ROIs are stored in a CSV file.

The tool is supposed to be run from the command line, as the control commands are entered there.

*Control commands*

* Press `q` or `Esc` to exit editing and save the config file.
* Press `r` to remove the last rectangle.

Run `python select_ROIs.py -h` for details.

### annotate ROIS

Script `annotate_ROIs.py` is used to specify the type of content for each rectangle.

The workflow is designed in a way that you can navigate over specified ROIs and assign them the expected type of their content.
This is done by pressing appropriate control commands.

*Control commands*

* Press `q` or `Esc` to exit editing and save the config file.
* Press `h` to add "Handwritten" type to the current ROI.
* Press `c` to add "Checkbox" type to the current ROI.
* Press `b` to add "Barcode" type to the current ROI.
* Press `r` or `d` to delete the type from the current ROI.
* Press `v` to enter the variable name.
* Press an arrow to navigate through ROIs (only left and right for now).

Run `python select_ROIs.py -h` for details.

## process logsheet

Script `process_logsheet.py` is used to extract values from specified ROIs.

This is the crucial step that applies various techniques to extract the information as precisely as possible.
It can process one logsheet at a time, given the template and config files.

Run `python select_ROIs.py -h` for details.
