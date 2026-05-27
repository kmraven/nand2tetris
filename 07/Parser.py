from enum import Enum
from typing import TextIO, Optional, Union, List


class CommandType(Enum):
    C_ARITHMETIC = 'C_ARITHMETIC'
    C_PUSH = 'C_PUSH'
    C_POP = 'C_POP'
    C_LABEL = 'C_LABEL'
    C_GOTO = 'C_GOTO'
    C_IF = 'C_IF'
    C_FUNCTION = 'C_FUNCTION'
    C_RETURN = 'C_RETURN'
    C_CALL = 'C_CALL'


class Parser:
    def __init__(self, vm_file: TextIO):
        self.vm_file: TextIO = vm_file
        self.vm_file.seek(0)
        self.current_command: str = ''
        self.current_command_type: Optional[CommandType] = None
    
    def advance(self) -> None:
        self.current_command = self.vm_file.readline()
        if self.current_command == '':
            raise StopIteration("No more lines to read")
        self.current_command = self.current_command.strip()  # Remove leading/trailing whitespace and \n
        if self.current_command.startswith('//') or not self.current_command:  # comment or empty line
            return self.advance()
        # TODO : Validate command format
        self.current_command_type = self.command_type()
    
    def command_type(self) -> CommandType:
        assert self.current_command is not None, "No current command to determine type"
        line = self.current_command
        if line.startswith('push'):
            return CommandType.C_PUSH
        elif line.startswith('pop'):
            return CommandType.C_POP
        elif line.startswith(('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not')):
            return CommandType.C_ARITHMETIC
        else:
            raise ValueError(f"Line {self.vm_file.tell()} : Unknown command type")
    
    def arg1(self) -> str:
        assert self.current_command_type != CommandType.C_RETURN
        if self.current_command_type == CommandType.C_ARITHMETIC:
            return self.current_command
        line = self.current_command
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Line {self.vm_file.tell()} : Missing argument for command")
        return ' '.join(parts[:2])

    def arg2(self) -> int:
        assert self.current_command_type in {CommandType.C_PUSH, CommandType.C_POP, CommandType.C_FUNCTION, CommandType.C_CALL}
        line = self.current_command
        parts = line.split()
        if len(parts) < 3:
            raise ValueError(f"Line {self.vm_file.tell()} : Missing second argument for command")
        try:
            return int(parts[2])
        except ValueError:
            raise ValueError(f"Line {self.vm_file.tell()} : Second argument must be an integer")
    