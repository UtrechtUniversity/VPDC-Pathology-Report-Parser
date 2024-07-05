# VPDC Pathology Report Parser

## Description

The script extracts data from standard pathology reports from the UU's VDPC ([Veterinair Pathologisch Diagnostisch Centrum](https://www.uu.nl/onderzoek/veterinair-pathologisch-diagnostisch-centrum)), provided as PDF files.

## Prerequisites

Requires Python 3.0 or higher, and [pypdfium](https://pypi.org/project/pypdfium2/) for PDF parsing (run `pip install -r requirements.txt` to install).

## Usage

```bash
usage: PathologicalReportParser.py [-h] -i INPUT_PATH

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_PATH, --input-path INPUT_PATH
                        Folder with veterinary report PDF's (can be recursive)
```
Example:
```bash
python VetReportParser.py -i '/data/reports/'
```
The program will traverse the folder `/data/reports/` and all its subfolders, find all PDF's, and try to parse them. It is assumed all PDF files are veterinary reports; anything else will probably cause an error.

## Output

The program will output a .tsv file in the input path; the file name will include the current date and time (example: `data--2024-07-05_10-37-36.tsv`).

The output file will for each input file contain the following data points, if they were present in the document:

_Meta data (blue boxes at the top of the document)_
+ `Bestand` (file name)
+ `Ordernr` (order number)
+ `Datum order` (order date)
+ `Datum def` (definitive date)
+ `Soort/ras` (species)
+ `DoB hond` (date of birth dog)
+ `Chipnummer` (chipnumber) 
+ `Geslacht` (gender)

_Main data_
+ `Klinische gegevens` (clinical data)
+ `Ingezonden materialen` (submitted materials)
+ `Conclusie` (conclusion)
+ `Macroscopie` (macroscopy)
+ `Microscopie` (mocroscopy)
+ `Verantwoordelijk` (responsible veterinarian)
+ `Opmerkingen` (remarks)