import argparse
from pathlib import Path
from googletrans import Translator
import csv
import os.path

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('--tbl', default='deltora_text_full.tbl')
args = parser.parse_args()

translator = Translator()

class Item:
    id: str
    name_jpn: str
    name_autotrans: str
    name_translated: str
    data: bytes

with open(args.tbl, 'r', encoding='utf-8') as f:
    tbl_data = f.read().splitlines()

decode_table = {}
for string_entry in tbl_data:
    if string_entry.startswith('#') or string_entry == '':
        continue
    vals = string_entry.split('=', 1)
    assert len(vals) == 2, f"Format error in table entry: \'{string_entry}\'"
    decode_table[vals[0].lower()] = vals[1]

with open(args.filename, 'rb') as f:
    filebytes = f.read()

items = list[Item]()
for i in range(0, len(filebytes), 300):
    id = filebytes[i+4:i+8].hex()
    name_bytes = filebytes[i+8:i+180]
    data = filebytes[i+180:i+300].hex()
    name = ''
    for j in range(0, len(name_bytes), 2):
        char = name_bytes[j:j+2].hex()
        if char == '0000':
            continue
        elif char in decode_table:
            name += decode_table[char]            
        else:
            name += '#' + char
    item = Item()
    item.id = id
    item.name_jpn = name
    item.name_autotrans = translator.translate(name).text
    item.name_translated = name
    item.data = data
    print(item.name_autotrans)
    items.append(item)

out_file = Path(args.filename).with_suffix('.tsv')
with open(out_file, 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(['ID', 'Japanese', 'Google Translate', 'Translated', 'Data'])
    for item in items:
        writer.writerow([f"\"{item.id}\"", item.name_jpn, item.name_autotrans, item.name_translated, item.data])