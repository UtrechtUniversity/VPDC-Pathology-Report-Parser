# VPDC Pathology Report Parser

## Description

The script extracts data from standard pathology reports from the UU's VDPC ([Veterinair Pathologisch Diagnostisch Centrum](https://www.uu.nl/onderzoek/veterinair-pathologisch-diagnostisch-centrum)), provided as PDF files.

The script was written using pathologies all relating to dogs, but theoretically it should also work for reports on other animals (untested). See the Usage-section for details.


## Prerequisites

Requires Python 3.9 or higher, and [pypdfium](https://pypi.org/project/pypdfium2/) for PDF parsing (run `pip install -r requirements.txt` to install).

## Usage

```bash
usage: PathologicalReportParser.py [-h] -i INPUT_PATH [--animal-type ANIMAL_TYPE]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_PATH, --input-path INPUT_PATH
                        Folder with veterinary report PDF's (can be recursive)
  --animal-type ANIMAL_TYPE
                        Optional; defaults to 'hond'
```

Example:
```bash
python PathologicalReportParser.py -i '/data/reports/'
```
The program will traverse the folder `/data/reports/` and all its subfolders, find all PDF's, and try to parse them. It is assumed all PDF files are veterinary reports; anything else will probably generate errors.

When using the script for other types of animal, the type of animal has to correspond to the wording in the document (case insensitive). Open a report and look up the value of the field 'Soort/Ras' in the purple box at the top right of the page, and use the part before the slash. 

For instance, if the report says : `Soort/Ras: Kat/Perzische korthaar` the program would have to be run as:
```bash
python PathologicalReportParser.py -i '/data/reports/' --animal-type kat
```
If you have reports on different types of animals, sort them by animal first, and then run the script independently for each set of documents.


## Output

The program will output a .tsv file in the input path; the file name will include the current date and time (example: `data--2024-07-05_10-37-36.tsv`).

The output file will for each input file contain the following data points, if they were present in the document:

_Meta data (purple boxes at the top of the document)_
+ `Bestand` (file name)
+ `Ordernr` (order number)
+ `Datum order` (order date)
+ `Datum def` (definitive date)
+ `Soort/ras` (species)
+ `Geboortedatum` (date of birth)
+ `Chipnummer` (chipnumber) 
+ `Geslacht` (gender)

_Main data_
+ `Klinische gegevens` (clinical data)
+ `Ingezonden materialen` (submitted materials)
+ `Conclusie` (conclusion)
+ `Macroscopie` (macroscopy)
+ `Microscopie` (microscopy)
+ `Verantwoordelijk` (responsible veterinarian)
+ `Opmerkingen` (remarks)

