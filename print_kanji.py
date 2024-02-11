import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--tbl', default='deltora_text_full.tbl')
args = parser.parse_args()

with open(args.tbl, 'r', encoding='utf-8') as f:
    tbl_data = f.read().splitlines()

decode_table = {}
encode_table = {}
for entry in tbl_data:
    if entry.startswith('#') or entry =='':
        continue
    vals = entry.split('=', 1)
    assert len(vals) == 2, f"Format error in table entry: \'{entry}\'"
    decode_table[vals[0].lower()] = vals[1]
    if vals[1] in encode_table:
        print(f'Duplicate encoding detected for {vals[1]} ({encode_table[vals[1]]} & {vals[0]})')
    encode_table[vals[1]] = vals[0].lower()

for block in range(0x5):
    for row in range(0x10):
        line = f'{row:x}#0{block:x}: '
        for col in range(0x10):
            key = f'{row:x}{col:x}0{block:x}'
            if key in decode_table:
                line += decode_table[key]
            else:
                line += '　'
        print(line)