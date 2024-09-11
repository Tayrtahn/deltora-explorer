import argparse
import os.path
import csv
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('--tbl', default='deltora_text_full.tbl')
args = parser.parse_args()

class Item:
    id: int
    name_jpn: str
    name_autotrans: str
    name_translated: str
    data: bytes

with open(args.tbl, 'r', encoding='utf-8') as f:
    tbl_data = f.read().splitlines()

encode_table = {}
for entry in tbl_data:
    if entry.startswith('#') or entry =='':
        continue
    vals = entry.split('=', 1)
    assert len(vals) == 2, f"Format error in table entry: \'{entry}\'"
    if vals[1] in encode_table:
        print(f'Duplicate encoding detected for {vals[1]} ({encode_table[vals[1]]} & {vals[0]})')
    encode_table[vals[1]] = vals[0].lower()

encoded_items = []
with open(args.filename, newline='') as f:
    strings = csv.reader(f, delimiter='\t')
    table_head = ''
    for string in strings:
        if table_head == '':
            table_head = string
            continue
        item = Item()
        item.id = string[0].strip('"')
        item.name_jpn = string[1]
        item.name_autotrans = string[2]
        item.name_translated = string[3]
        print(item.name_translated)
        item.data = string[4]
        string_bytes = bytearray()
        string_bytes.extend(bytes.fromhex('00000000'))
        string_bytes.extend(bytes.fromhex(item.id))
        name_bytes = bytearray()
        i = 0
        name_length = 0
        text = item.name_translated
        while True:
            if name_length > 10:
                raise Exception(f"Name of item #{item.id} ({item.name_translated}) is too long!")
            if i >= len(text):
                break
            char = text[i]
            if char == '#':
                code = text[i+1:i+5]
                name_bytes.extend(bytes.fromhex(code))
                i += 4
            elif char in encode_table:
                name_bytes.extend(bytes.fromhex(encode_table[char]))
            i += 1
            name_length += 1
        string_bytes.extend(name_bytes)
        string_bytes = string_bytes.ljust(180, bytes.fromhex('00'))
        string_bytes.extend(bytes.fromhex(item.data))
        encoded_items.append(string_bytes)

out_file = Path(args.filename).with_suffix('.bin')
with open(out_file, 'wb') as f:
    for item in encoded_items:
        f.write(item)