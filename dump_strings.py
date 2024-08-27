import argparse
from pathlib import Path
from googletrans import Translator
import csv
import os.path

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('--tbl', default='deltora_text_full.tbl')
parser.add_argument('--tsv', action='store_true')
parser.add_argument('--raw')
args = parser.parse_args()

translator = Translator()

class StringEntry:
    header: str
    japanese: str
    autotrans: str
    translated: str

with open(args.tbl, 'r', encoding='utf-8') as f:
    tbl_data = f.read().splitlines()

decode_table = {}
for string_entry in tbl_data:
    if string_entry.startswith('#') or string_entry =='':
        continue
    vals = string_entry.split('=', 1)
    assert len(vals) == 2, f"Format error in table entry: \'{string_entry}\'"
    decode_table[vals[0].lower()] = vals[1]

with open(args.filename, 'rb') as f:
    filebytes = f.read()

offsets = []
i = 0
prev = 0
while True:
    offset = int.from_bytes(filebytes[i:i+4], 'little')
    if offset > len(filebytes) or offset <= prev:
        break
    offsets.append(offset)
    prev = offset
    i += 4

string_entries = list[StringEntry]()
n = 0
for offset in offsets:
    start = filebytes[offset:offset+4].hex()
    i = offset + 4
    string = ''
    while True:
        char = filebytes[i:i+2].hex()
        if char == 'fdff':
            break
        if char in decode_table:
            string += decode_table[char]
        else:
            string += '#' + char
        i += 2
    autotrans = translator.translate(string).text
    print(str(n) + ':' + start + ':' + string + ':' + autotrans)
    string_entry = StringEntry()
    string_entry.header = start
    string_entry.japanese = string
    string_entry.autotrans = autotrans
    string_entry.translated = ''
    string_entries.append(string_entry)
    n += 1

def check_overwrite(filename) -> bool:
    if os.path.isfile(filename):
        overwrite = input('Overwrite ok? y/N: ')
        if overwrite.lower() == 'y':
            return True
        return False
    # File doesn't exist, so we're clear to write
    return True

def write_strings(entries: list[StringEntry], filename):
    out_file = Path(args.filename).with_suffix('.txt')
    if not check_overwrite(out_file):
        return

    with open(out_file, 'w') as f:
        for entry in entries:
            f.write(entry.header + '#' + entry.string + "\n")
    print(f'Wrote to {out_file}')

def write_tsv(entries: list[StringEntry], filename):
    out_file = Path(args.filename).with_suffix('.tsv')
    if not check_overwrite(out_file):
        return
    
    with open(out_file, 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Header', 'Japanese', 'Google Translate', "Translated"])
        for entry in entries:
            writer.writerow([f"\"{entry.header}\"", entry.japanese, entry.autotrans, entry.japanese])
    print(f'Wrote to {out_file}')

if args.tsv:
    write_tsv(string_entries, args.filename)
else:
    write_strings(string_entries, args.filename)

