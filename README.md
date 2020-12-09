# MedLinker-Social
Adaptation of [MedLinker (ECIR 2020)](https://github.com/danlou/MedLinker) to the Social Domain.

Project Homepage: http://danlou.github.io/medlinker-social/

Adaptation Report: http://danlou.github.io/files/papers/medlinker_social_report.pdf

## Installation

### Prepare Environment

This project was developed on Python 3.6.5 from Anaconda distribution v4.6.14. As such, the pip requirements assume you already have packages that are included with Anaconda (numpy, etc.).
After cloning the repository, we recommend creating and activating a new environment to avoid any conflicts with existing installations in your system:

```bash
$ git clone https://github.com/danlou/MedLinker-Social.git
$ cd MedLinker-Social
$ conda create -n MedLinker-Social python=3.6.5
$ conda activate MedLinker-Social
# $ conda deactivate  # to exit environment when done with project
```

### Additional Packages

To install additional packages used by this project (YAKE and SimString) run:

```bash
$ pip install -r requirements.txt
```

If you want to load fasttext .bin models (as used in the tutorial), you'll also need to follow [these instructions](https://github.com/facebookresearch/fastText#building-fasttext-for-python) to install fasttext for Python.


### Download Data and Models

To use our linker, you'll need to download and unzip [umls_2020_aa_cat0129_ext.zip](https://drive.google.com/file/d/1x0QpWq7wttwNkBY5DEAtyv8T9ECImrjX/view?usp=sharing) into data/SimString. The linker uses additional files of smaller sizes, but these should already be included in this repository.

We also release a version of the linker without the aliases we added to UMLS. If you're interested in that version of the linker, then download and unzip [umls_2020_aa_cat0129.zip](https://drive.google.com/file/d/1fTJspMtiPfGTw1Z4ZDoIPRyUllMSvbqL/view?usp=sharing) instead, also into data/SimString.

In case you're just interested in UMLS data, we recommend using [scispacy](https://github.com/allenai/scispacy)'s version, which we also used for this project.

You may also find corpora and embeddings we use in the tutorial and report at the [reddit](https://drive.google.com/drive/folders/1TtKHMPPWHCjpkZE7iv8ta2RsZbGXAb6Q?usp=sharing) and [europmc](https://drive.google.com/drive/folders/1ngdAqgfRToV7s4NJpZYWIovN0uCmPB0u?usp=sharing) folders.

## Using MedLinker-Social

Follow the tutorial at: https://github.com/danlou/MedLinker-Social/blob/main/tutorial.ipynb
