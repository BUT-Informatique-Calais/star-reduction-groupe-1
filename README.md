[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/zP0O23M7)

# Project Documentation

## Installation

### Virtual Environment

It is recommended to create a virtual environment before installing dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Dependencies

```bash
pip install -r requirements.txt
```

Or install dependencies manually:

```bash
pip install [package-name]
```

## Usage

### Command Line

```bash
python main.py [arguments]
```

## Requirements

- Python 3.8+
- See `requirements.txt` for full dependency list

## PHASE 3 - Star Reduction with Machine Learning Mask (Starnet in SIRIL) - (Linux)

### Objectif

    Use a pre-trained model (StarNet) to segment the stars and completely separate them from the sky background before processing.

### What is Starnet ?

    StarNet is a program who use a neuronal network (Machine LEArning) for remove the stars of an astro picture.

### Why make that :

    In phase 2, we have a mask "M" by classical method (DAOStarFinder)
    In phase 3, we replace it (the mask) by an ML method
    - StarNet (ML) generate :
    - one image starless
    - one starmask
    - After that we re-use the same mathematical method where in phase 2.

### Requirements :

- Linux Mint (or Ubuntu)
- Siril downloaded
- StarNet **CLI** downloaded

### 1. Download Siril (Linux)

The documentation recommend PPA on Ubuntu/Linux Mint

```bash
sudo add-apt-repository ppa:lock042/siril
sudo apt-get update
sudo apt-get install siril
```

You got Siril

### 2. Create directories

You will create two directories - star_reduction : The directory where siril will automatically save the files fit (starless,starmask)(to be create into folder or project). - StarNetCLI : The directory will Starnet CLI program will be stock (because siril doesn't install it)

```bash
mkdir -p ~star_reduction
mkdir -p ~StarNetCLI

```

### 3. Install StarNetCLI

Url : https://www.starnetastro.com/download/
Here we have the url to download the good CLI .zip

- WINDOWS : Fresh install: StarNetv2CLI_Win.zip
- MacOS -> Fresh install: StarNetv2CLI_MacOS.zip
- Linux -> Fresh install: StarNetv2CLI_linux.zip

Place and unzip in : `/home/user/astro`
Make the files executables :

```bash
chmod +x ~/astro/StarNetCLI/*
```

### 4. In Siril (LAunch SIRIL)

#### 4.0 Set the CLI program of Starnet

- Top-right: **click the hamburger menu -> Preferences -> Miscellaneous -> Software locations**
- Set **Starnet++** file in **Starnet executable** apply and ok.

#### 4.1 Define working directory

- Top-LEFT: **/home/user/astro/star_reduction**

#### 4.2 Open file FITS

- Click on open and select the file **.FITS** you want use

### 5 - Launch Starnet

In the bottom of Siril you have a CLI :
write :

```bash
starnet -stretch
```

-stretch : Increase the luminosity by stretching the pictures (especially for linear pictures)

## Examples files

Example files are located in the `examples/` directory. You can run the scripts with these files to see how they work.

- Example 1 : `examples/HorseHead.fits` (Black and whiteFITS image file for testing)
- Example 2 : `examples/test_M31_linear.fits` (Color FITS image file for testing)
- Example 3 : `examples/test_M31_raw.fits` (Color FITS image file for testing)