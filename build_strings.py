import argparse
import os.path
import csv
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('--tbl', default='deltora_text_full.tbl')
args = parser.parse_args()

class StringEntry:
    string: str
    japanese: str
    autotrans: str
    translated: str

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

def read_txt(filename: str):
    encoded_strings = []
    with open(filename, 'r') as f:
        strings = f.readlines()
    print(f'Read {len(strings)} lines')
    for string in strings:
        string_bytes = bytearray()
        start = bytes.fromhex(string[0:8])
        string_bytes.extend(start)
        i = 9
        while True:
            if i >= len(string):
                break
            char = string[i]
            if char == '#':
                code = string[i+1:i+5]
                string_bytes.extend(bytes.fromhex(code))
                i += 4
            elif char in encode_table:
                string_bytes.extend(bytes.fromhex(encode_table[char]))
            i += 1
        string_bytes.extend(bytes.fromhex('fdff'))
        encoded_strings.append(string_bytes)
    return encoded_strings

def read_tsv(filename: str):
    encoded_strings = []
    with open(filename, newline='') as f:
        strings = csv.reader(f, delimiter='\t')
        table_head = ''
        for string in strings:
            if table_head == '':
                table_head = string
                continue
            entry = StringEntry()
            entry.header = string[0].strip('"').rjust(8, '0')
            entry.japanese = string[1]
            entry.autotrans = string[2]
            entry.translated = string[3]
            string_bytes = bytearray()
            start = bytes.fromhex(entry.header)
            string_bytes.extend(start)
            i = 0
            text = entry.translated
            while True:
                if i >= len(text):
                    break
                char = text[i]
                if char == '#':
                    code = text[i+1:i+5]
                    string_bytes.extend(bytes.fromhex(code))
                    i += 4
                elif char in encode_table:
                    string_bytes.extend(bytes.fromhex(encode_table[char]))
                i += 1
            string_bytes.extend(bytes.fromhex('fdff'))
            encoded_strings.append(string_bytes)
    return encoded_strings

def check_overwrite(filename) -> bool:
    if os.path.isfile(filename):
        overwrite = input('Overwrite ok? y/N: ')
        if overwrite.lower() == 'y':
            return True
        return False
    # File doesn't exist, so we're clear to write
    return True

encoded_strings = read_tsv(args.filename)
out_file = Path(args.filename).with_suffix('.bin')

if check_overwrite(out_file):
    with open(out_file, 'wb') as f:
        offset = len(encoded_strings) * 4
        for string in encoded_strings:
            offset_bytes = offset.to_bytes(4, byteorder='little')
            offset += len(string)
            f.write(offset_bytes)

        for string in encoded_strings:
            f.write(string)
    print(f'Wrote to {out_file}')