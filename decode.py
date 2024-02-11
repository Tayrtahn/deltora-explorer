import argparse

parser = argparse.ArgumentParser()
parser.add_argument('text')
parser.add_argument('--tbl', default='deltora_text_full.tbl')
args = parser.parse_args()

with open(args.tbl, 'r', encoding='utf-8') as f:
    tbl_data = f.read().splitlines()

decode_table = {}
for string_entry in tbl_data:
    if string_entry.startswith('#') or string_entry =='':
        continue
    vals = string_entry.split('=', 1)
    assert len(vals) == 2, f"Format error in table entry: \'{string_entry}\'"
    decode_table[vals[0].lower()] = vals[1]

string = ''
for i in range(0, len(args.text), 4):
    code = args.text[i:i+4]
    if code.lower() in decode_table:
        character = decode_table[code.lower()]
    else:
        character = '#'
    string += character

print(string)