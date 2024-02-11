from scr0 import ScriptFile
import os.path
import struct

class FileEntry:
    name: str
    offset: int
    length: int
    magic: str
    data: bytes
    extension: str

class FileData:
    files: list[FileEntry]
    data: bytes

    def __init__(self, data: bytes = None):
        self.files = []

        if (data):
            self._initFromData(data)


    def _initFromData(self, filedata: bytes):
        self.files.clear()
        self.data = filedata

        file_count = int.from_bytes(filedata[8:12], 'little')
        for i in range(file_count):
            mem = (i * 8) + 16
            offset = int.from_bytes(filedata[mem:mem+4], 'little') * 4
            length = int.from_bytes(filedata[mem+4:mem+8], 'little')
            end = offset + length
            data = filedata[offset:end]
            extension = 'bin'
            magic = b'UNKN'
            if (data[:4].isalnum()):
                magic = data[:4].decode('ascii')
                extension = magic[::-1]
                if extension == '0RCS':
                    extension = 'SCR'
                if extension == '0DMB':
                    extension = 'BMD'

            file = FileEntry()
            file.name = f'{str(i).zfill(4)} - {str(offset).zfill(8)}'
            file.offset = offset
            file.length = length
            file.data = data
            file.magic = magic
            file.extension = extension

            self.files.append(file)

    def initFromFiles(self, files_dir: str):
        self.files.clear()

        files = sorted(os.listdir(files_dir))
        filtered = filter(lambda f: not f.startswith('.'), files)
        files = list(filtered)
        print(f'Found {len(files)} files')
        for file in files:
            if os.path.isfile(os.path.join(files_dir, file)):
                with open(os.path.join(files_dir, file), 'rb') as f:
                    entry = FileEntry()
                    entry.data = f.read()
                    entry.length = len(entry.data)
                    entry.name = file
                    self.files.append(entry)

        self.rebuild_data()


    def apply_overrides(self, overrides_dir: str):
        if os.path.isdir(overrides_dir):
            overrides = list(filter(lambda f: not f.startswith('.'), os.listdir(overrides_dir)))
            print(f'Found {len(overrides)} overrides')
            for i in range((len(self.files))):
                filename = f'{self.files[i].name}.{self.files[i].extension}'
                for override in overrides:
                    if os.path.isfile(os.path.join(overrides_dir, override)):
                        if filename == override:
                            print(f'Replacing {override} at index {i}')
                            with open(os.path.join(overrides_dir, override), 'rb') as f:
                                entry = FileEntry()
                                entry.data = f.read()
                                entry.length = len(entry.data)
                                self.files[i] = entry
        self.rebuild_data()


    def rebuild_data(self):
        entry_count = len(self.files)
        offset = 16 + entry_count * 8

        self.data = bytearray()
        self.data.extend(bytes.fromhex('4C462032'))
        self.data.extend(struct.pack('<I', int(offset/4)))
        self.data.extend(struct.pack('<I', len(self.files))) # File count
        self.data.extend(bytes.fromhex('10000000'))

        def align(alignment: int, fill: bytes = b'\0') -> None:
            if len(self.data) % alignment:
                extra = len(self.data) % alignment
                needed = alignment - extra
                self.data.extend(fill * needed)
        
        # Each entry is two 32-bit values: offset and length
        for f in self.files:
            #print(offset)
            self.data.extend(struct.pack('<I', int(offset / 4))) # Offset
            self.data.extend(struct.pack('<I', f.length)) # Length
            offset += f.length
            if f.length % 4:
                extra = f.length % 4
                offset += 4 - extra

        for f in self.files:
            self.data.extend(f.data)
            align(4)


    def exportFiles(self, files_dir: str):
        if not os.path.isdir(files_dir):
            os.mkdir(files_dir)
        i = 0
        for file in self.files:
            with open(f'./{files_dir}/{file.name}', 'wb') as f:
                f.write(file.data)
                i += 1


    def printTest(self):
        for f in self.files:
            if f.magic == b"SCR0":
                dat = ScriptFile(f.data)
                for c in dat.commands:
                    print(c.name)
                print("=========")
            #print(f'{hex(f.offset)} \t {f.length} \t\t {f.magic}')


    def calculateGaps(self):
        last_end = self.files[0].offset # Skip over the index
        for f in self.files:
            gap = f.offset - last_end
            data = self.data[last_end:f.offset]
            last_end = f.offset + f.length
            print(f'{f.offset} - {gap} - {f.length} - {data.hex()}')


    def exportCSV(self):
        with open('info.csv', 'w') as f:
            f.write('index,offset,length,extension\n')
            index = 0
            for file in self.files:
                f.write(f'{index},{file.offset},{file.length},{file.extension}\n')
                index += 1