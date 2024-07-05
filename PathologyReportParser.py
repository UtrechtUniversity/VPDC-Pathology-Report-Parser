import argparse
import csv
import os
import pypdfium2 as pdfium
import re
from datetime import datetime
from pathlib import Path

class PathologyReportParser:

    meta_categories_1 = ['Afnamedatum', 'Aanvrager', 'Ordernummer', 'Relatiecode', 'Clinicus', 'Uw referentie', ':']
    meta_categories_2 = ['Geboortedatum', 'Diernaam', 'Soort/Ras', 'Geslacht', 'Eigenaar', ':']

    def __init__(self, animal_type='hond'):
        self.animal_type = animal_type

    def read_file(self, filename):
        self.pdf = pdfium.PdfDocument(filename)
        self.file_name = os.path.basename(filename)

    def get_data(self):
        meta = self.get_meta_data(self.pdf[0])
        data = self.get_main_data()
        return meta, data

    def get_meta_data(self, page):
        # get the data from the purple boxes at the top of the page

        # # use the bitmap to get the coordinates of the boxes at the top 
        # # of the page (be aware that the in the PDF [0,0] is bottom left)
        # bitmap = page.render(
        #     scale = 1,    # 72dpi resolution
        # )
        # pil_image = bitmap.to_pil()
        # pil_image.show()
        # pil_image.save('./page.bmp')

        textpage = page.get_textpage()

        ordernr = ''
        date_order = ''
        date_def = ''

        animal_dob = ''
        animal_chipnummer = ''
        animal_gender = ''
        animal_species = ''
        names = []

        #l,b,r,t
        box1_page_1 = [26,612,294,733]
        # box1_page_2 = [26,700,294,817]

        data = textpage.get_text_bounded(*box1_page_1).splitlines()
        data = list(filter(lambda x: x.strip() not in self.meta_categories_1, data))

        p_ordernr = re.compile("\d{9,10}")
        p_def_date = re.compile("datum def\.?", re.IGNORECASE)

        dates = []

        for d in data:

            if p_ordernr.match(d):
                ordernr = d.strip()
                continue

            if 'datum def' in d.lower():
                d = p_def_date.sub('', d).strip()

            try:
                some_date = datetime.strptime(d,"%d-%m-%Y")
                dates.append(some_date)
                continue
            except:
                pass

        if len(dates)==0:
            date_order = None
            date_def = None
        elif len(dates)==1:
            date_def = dates[0]
        elif dates[0]<dates[1]:
            date_order = dates[0]
            date_def = dates[1]
        else:
            date_order = dates[1]
            date_def = dates[0]

        box2_page_1 = [303,612,568,733]
        # box2_page_2 = [297,700,562,815]
        data = textpage.get_text_bounded(*box2_page_1).splitlines()
        data = list(filter(lambda x: x.strip() not in self.meta_categories_2, data))

        p_chipnr = re.compile("chipnummer", re.IGNORECASE)
        s_animal = self.animal_type

        for d in data:
            if 'chipnummer' in d.lower():
                animal_chipnummer = p_chipnr.sub('', d).strip()
                continue

            try:
                animal_dob = datetime.strptime(d,"%d-%m-%Y")
                continue
            except:
                pass

            for g in ['mannelijk', 'vrouwelijk', 'man', 'vrouw', 'onbekend']:
                if g.lower() in d.lower():
                    animal_gender = d
                    break
            if len(animal_gender)>0:
                continue

            if d[:len(s_animal)].lower()==s_animal:
                animal_species = d
                continue

            names.append(d)

        out = {
            'Bestand': self.file_name,
            'Ordernr': ordernr,
            'Datum order': date_order,
            'Datum def': date_def,
            'Soort/ras': animal_species,
            'Geboortedatum': animal_dob, 
            'Chipnummer': animal_chipnummer,
            'Geslacht': animal_gender
            }

        return out

    def get_main_data(self):
        # get the data from the various sections in the document

        i = 0
        all_text = ''
        while True:
            try:
                page = self.pdf[i]
                textpage = page.get_textpage()
                all_text = f"{all_text}\n{textpage.get_text_range()}"
                i += 1
            except:
                break

        document_headers = ['Klinische gegevens', 'Ingezonden materialen', 'Conclusie', 'Macroscopie', 
                            'Microscopie', 'Verantwoordelijk', 'Opmerkingen']

        data = {}
        lines = []
        prev = None
        for line in [x.strip() for x in all_text.splitlines()]:

            if line[:4]=='Pag.':
                continue

            if line in document_headers:
                if prev is not None:
                    data[prev] = " ".join(lines)
                    lines = []
                data[line] = []
                prev = line
                del document_headers[document_headers.index(line)]
            elif prev:
                for cat in self.meta_categories_1 + self.meta_categories_2:
                    if line[:len(cat)]==cat:
                        continue
                else:
                    lines.append(line)
                    continue
            
        data[prev] = " ".join(lines)

        return data


if __name__=="__main__":

    parser=argparse.ArgumentParser()
    parser.add_argument('-i', '--input-path', type=str, required=True, help='Folder with veterinary report PDF\'s (can be recursive)')
    parser.add_argument('--animal-type', type=str, default='hond')
    args=parser.parse_args()

    prp = PathologyReportParser(animal_type=args.animal_type)
    root = args.input_path

    data = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            file = Path(os.path.join(path, name))
            print(f"Processing {file}")
            if file.suffix==".pdf":
                prp.read_file(Path(root) / file)
                meta, main = prp.get_data()
                data.append(meta | main)

    fieldnames = list(data[0].keys())
    outfile = root + f"data--{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.tsv"
    with open(outfile, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for output in data:
            writer.writerow(output)

    print(f"Wrote data to {outfile}")