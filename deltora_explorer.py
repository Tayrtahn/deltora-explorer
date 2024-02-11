import os.path
import ndspy.rom
import ndspy.lz10
import argparse
import pathlib

from filedata import FileData
from scr0 import ScriptFile

def unpack(args):
    filedata = get_filedata(args.inrom)

    with open('FILEDATA.BIN', 'wb') as f:
        f.write(filedata.data)
    print('Wrote FILEDATA.BIN to disk')

    filedata.exportFiles(args.filesdir)
    print(f'Exported files to {pathlib.Path(args.filesdir).absolute()}')


def pack(args):
    filedata = get_filedata(args.inrom)
    filedata.apply_overrides(args.overrides)

    rom = ndspy.rom.NintendoDSRom.fromFile(args.inrom)

    rom.setFileByName('FILEDATA.BIN', filedata.data)
    print("Packed FILEDATA.BIN")

    rom.saveToFile(args.outrom)
    print(f'Saved ROM to {args.outrom}')


def gaps(args):
    filedata = get_filedata(args.rom)
    filedata.calculateGaps()


def csv(args):
    filedata = get_filedata(args.rom)
    filedata.exportCSV()


def get_filedata(romname: str) -> FileData:
    if not os.path.isfile(romname):
        print(f'Unable to locate rom file \'{romname}\'')
        exit(1)

    rom = ndspy.rom.NintendoDSRom.fromFile(romname)
    print(f'Loaded ROM data from {romname}')
    
    filedata = rom.getFileByName('FILEDATA.BIN')
    print('Extracted FILEDATA.BIN from rom')

    return FileData(filedata)


default_files_path = pathlib.Path('files')
default_override_path = pathlib.Path('overrides')
default_in_rom_name = 'Deltora Quest - Nanatsu no Houseki (Japan).nds'
default_out_rom_name = 'deltora_edited.nds'

parser = argparse.ArgumentParser(prog='Deltora Explorer')
subparsers = parser.add_subparsers(required=True)

pack_parser = subparsers.add_parser('pack')
pack_parser.add_argument('--overrides', type=pathlib.Path, default=default_override_path)
pack_parser.add_argument('--inrom', type=str, default=default_in_rom_name)
pack_parser.add_argument('--outrom', type=str, default=default_out_rom_name)
pack_parser.set_defaults(func=pack)

unpack_parser = subparsers.add_parser('unpack')
unpack_parser.add_argument('--filesdir', type=pathlib.Path, default=default_files_path)
unpack_parser.add_argument('--inrom', type=str, default=default_in_rom_name)
unpack_parser.set_defaults(func=unpack)

gaps_parser = subparsers.add_parser('gaps')
gaps_parser.add_argument('--rom', default=default_in_rom_name)
gaps_parser.set_defaults(func=gaps)

csv_parser = subparsers.add_parser('csv')
csv_parser.add_argument('--rom', default=default_in_rom_name)


args = parser.parse_args()
args.func(args)
