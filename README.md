# Deltora Explorer
A set of Python tools for modifying data in Deltora Quest - Nanatsu no Houseki

## deltora_explorer.py
Used to pack/unpack data files from/to the main ROM file. Run the **unpack** command and pass a legitimately acquired ROM of _Deltora Quest - Nanatsu no Houseki_ to extract FILEDATA.BIN and generate the _files/_ directory containing all the data of the game separated into individual files. If modified files are placed in a separate directory ("_overrides/_"), they will be used in place of the originals when running **pack** to rebuild the ROM file.

## dump_strings.py
Used to extract the dialogue strings from the .bin files produced by deltora_explorer.py. Outputs a text file with each line by default, add _--tsv_ as an argument to output as Tab-Separated Values instead. Each string is preceded by a 4-byte value that specifies which character is speaking, which portrait to use for them, and what sound to play, as well as other effects.

## build_strings.py
Used to convert edited dialogue strings back into the binary format used by the game. Run dump_strings.py, edit the resulting text file, then run build_strings.py to produce an edited .bin file that can be placed into _overrides/_ to pack back into an edited ROM file.

## deltora_text_full.tbl
Contains the complete character encoding used by text in the game. Used by dump_strings.py and build_strings.py The format is XXXX=Y, where XXXX is the hexidecimal representation of a two-byte value found in the raw binary, and Y is the representation to be used for viewing/editing. Unspecified patterns found in the binary will be transcribed in hex as #XXXX.

## decode.py
A small utility that can be used to convert a manually entered hex-encoded string into its unicode output, using deltora_text_full.tbl as a lookup. Helpful for hunting for encoded text in other files.

## print_kanji.py
Outputs the complete set of decoded characters from deltora_text_full.tbl, for testing purposes. This was used to compare the encoding with a reference image file found in the game.
