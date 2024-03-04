# formHTR
Handprint text recognition in form documents.

![Trec](https://github.com/grp-bork/formHTR/assets/15349569/c0789616-80d0-43c8-8693-d3d9f070511c)

# Installation

```
conda env create -f conda_env.yaml
```

The tool also requires [zbar](https://github.com/NaturalHistoryMuseum/pyzbar/issues/37) shared library installed.

# Usage

## Create ROIs

This functionality is split (for now) into two separate scripts.

### select ROIs

Script `select_ROIs.py` is used to find and define locations of regions of interest (ROIs) in the given PDF.

Generally, it is possible to draw ROIs (rectangles) manually but also to detect them automatically.
The coordinates of ROIs are stored in a JSON file.

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

### process logsheet

Script `process_logsheet.py` is used to extract values from specified ROIs.

This is the crucial step that applies various techniques to extract the information as precisely as possible.
It can process one logsheet at a time, given the template and config files.

Run `python select_ROIs.py -h` for details.

#### Credentials

The processing of logsheets is using external services requiring credentials to use them. Here we specify structure that is expected for credentials, always in JSON format.

__Google__

```
{
  "type": "service_account",
  "project_id": "theid",,
  "private_key_id": "thekey",
  "private_key": "-----BEGIN PRIVATE KEY-----anotherkey-----END PRIVATE KEY-----\n"
  "client_email": "emailaddress",
  "client_id": "id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "someurl",
  "universe_domain": "googleapis.com"
}
```

__Amazon__

```
{
    "ACCESS_KEY": "YOUR_KEY_ID_HERE",
    "SECRET_KEY": "YOUR_ACCESS_KEY_HERE",
    "REGION": "YOUR_REGION_NAME_HERE"
}
```

__Microsoft__

```
{
    "SUBSCRIPTION_KEY": "YOURKEYHERE",
    "ENDPOINT": "https://ENDPOINT"
}
```

---

## Testing

It is possible to test logsheet processing using dry run without credentials on data stored in `tests/`.

Run `python dry_processing.py -h` for details.
