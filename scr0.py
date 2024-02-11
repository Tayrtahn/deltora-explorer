class Section:
    offset: int
    name: str

class Command:
    offset: int
    name: str

class ScriptFile:
    bit_count: int
    v4: int
    v5: int
    sections: list[Section]
    commands: list[Command]

    def __init__(self, data: bytes):
        self.sections = []
        self.commands = []

        section_count = int.from_bytes(data[8:10], 'little')
        command_count = int.from_bytes(data[10:12], 'little')

        self.bit_count = int.from_bytes(data[12:16], 'little')
        self.v4 = int.from_bytes(data[16:24], 'little')
        self.v5 = int.from_bytes(data[24:32], 'little')

        for i in range(section_count):
            mem = i * 4 + 0x20
            section = Section()
            section.offset = int.from_bytes(data[mem:mem+4], 'little')
            self.sections.append(section)
        
        for i in range(command_count):
            mem = i * 4 + (section_count * 4 + 0x20) + 4
            command = Command()
            command.offset = int.from_bytes(data[mem:mem+4], 'little')
            command.name = data[command.offset+32:command.offset+32+16].decode()
            self.commands.append(command)