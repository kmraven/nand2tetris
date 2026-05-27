from enum import Enum
from typing import TextIO, Optional


class InstructionType(Enum):
    A_INSTRUCTION = 0
    C_INSTRUCTION = 1
    L_INSTRUCTION = 2


class Parser:
    def __init__(self, asm_file: TextIO):
        self.asm_file: TextIO = asm_file
        self.asm_file.seek(0)
        self.current_instruction: str = ''
        self.current_instruction_type: Optional[InstructionType] = None
        self.current_address: int = -1  # Regardless comment or empty line
    
    def reset(self) -> None:
        self.asm_file.seek(0)
        self.current_instruction = ''
        self.current_instruction_type = None
        self.current_address = -1
    
    def advance(self) -> None:
        self.current_instruction = self.asm_file.readline()
        if self.current_instruction == '':
            raise StopIteration("No more lines to read")
        self.current_instruction = self.current_instruction.strip()  # Remove leading/trailing whitespace and \n
        if self.current_instruction.startswith('//') or not self.current_instruction:  # comment or empty line
            return self.advance()
        # TODO : Validate instruction format
        self.current_instruction_type = self.instruction_type()
        if self.current_instruction_type != InstructionType.L_INSTRUCTION:
            self.current_address += 1
    
    def instruction_type(self) -> InstructionType:
        line = self.current_instruction
        if line.startswith('@'):
            return InstructionType.A_INSTRUCTION
        elif '=' in line or ';' in line:
            return InstructionType.C_INSTRUCTION
        elif line.startswith('(') and line.endswith(')'):
            return InstructionType.L_INSTRUCTION
        else:
            raise ValueError(f"Line {self.asm_file.tell()} : Unknown instruction type")
    
    def symbol(self) -> str:
        line = self.current_instruction
        if self.current_instruction_type == InstructionType.A_INSTRUCTION:
            return line[1:]
        elif self.current_instruction_type == InstructionType.L_INSTRUCTION:
            return line[1:-1]
        else:
            raise ValueError("Symbol not applicable for C instruction")
    
    def dest(self) -> str:
        line = self.current_instruction
        if self.current_instruction_type == InstructionType.C_INSTRUCTION:
            if '=' in line:
                return line.split('=')[0].strip()
            return ''
        raise ValueError("Dest not applicable for A or L instruction")

    def comp(self) -> str:
        line = self.current_instruction
        if self.current_instruction_type == InstructionType.C_INSTRUCTION:
            if '=' in line:
                comp_part = line.split('=')[1]
            else:
                comp_part = line.split(';')[0]
            return comp_part.strip()
        raise ValueError("Comp not applicable for A or L instruction")
    
    def jump(self) -> str:
        line = self.current_instruction
        if self.current_instruction_type == InstructionType.C_INSTRUCTION:
            if ';' in line:
                return line.split(';')[1].strip()
            return 'null'
        raise ValueError("Jump not applicable for A or L instruction")