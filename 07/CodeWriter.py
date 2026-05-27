
from typing import TextIO


class CodeWriter:

    NAME_DICT = {
            'argument': 'ARG',
            'local': 'LCL',
            'this': 'THIS',
            'that': 'THAT',
        }

    def __init__(self, asm_file: TextIO):
        self.asm_file: TextIO = asm_file
        self.asm_file.seek(0)
        self.static_dict: dict[int, int] = {}
        self.static_counter: int = 0
        self.symbol_counter: int = 0

    def write_arithmetic(self, command: str) -> None:
        assert command in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not')
        self.asm_file.write(f"// {command}\n")
        if command in ('add', 'sub', 'and', 'or'):
            # M: left, D: right
            if command == 'add':
                op = 'D+M'  # there is no operator for M+D in Hack assembly
            elif command == 'sub':
                op = 'M-D'
            elif command == 'and':
                op = 'D&M'
            elif command == 'or':
                op = 'D|M'
            asm = (
                "@SP",
                "AM=M-1",
                "D=M",
                "A=A-1",
                f"M={op}",
            )
        elif command in ('neg', 'not'):
            op = '-M' if command == 'neg' else '!M'
            asm = (
                "@SP",
                "A=M-1",
                f"M={op}",
            )
        elif command in ('eq', 'lt', 'gt'):
            op = 'JEQ' if command == 'eq' else 'JLT' if command == 'lt' else 'JGT'
            asm = (
                "@SP",
                "AM=M-1",
                "D=M",
                "A=A-1",
                "D=M-D",  # M: left, D: right
                f"@IF_TRUE_{self.symbol_counter}",
                f"D;{op}",
                "@SP",
                "A=M-1",
                "M=0",  # False
                f"@IF_END_{self.symbol_counter}",
                "0;JMP",
                f"(IF_TRUE_{self.symbol_counter})",
                "@SP",
                "A=M-1",
                "M=-1",  # True
                f"(IF_END_{self.symbol_counter})",
            )
            self.symbol_counter += 1
        else:
            raise ValueError(f"Unknown arithmetic command: {command}")
        self.asm_file.write("\n".join(asm) + "\n")
    
    def __get_asm_set_target_address(self, segment: str, index: int) -> tuple[str, ...]:
        assert segment in ('argument', 'local', 'static', 'this', 'that', 'pointer', 'temp')
        if segment in CodeWriter.NAME_DICT.keys():
            return (
                f"@{index}",
                "D=A",
                f"@{CodeWriter.NAME_DICT[segment]}",
                "A=D+M",
            )
        elif segment == 'pointer':
            assert index in (0, 1), "Pointer index must be 0 or 1"
            return (
                f"@{'THIS' if index == 0 else 'THAT'}",
            )
        elif segment == 'temp':
            assert 0 <= index < 8, "Temp index must be in range 0-7"
            return (
                f"@{index + 5}",
            )
        elif segment == 'static':
            if index not in self.static_dict.keys():
                self.static_dict[index] = self.static_counter
                self.static_counter += 1
            return (
                f"@{self.static_dict[index] + 16}",
            )
        else:
            raise ValueError(f"Unknown segment: {segment}")

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        assert command in ('push', 'pop')
        assert segment in ('argument', 'local', 'static', 'constant', 'this', 'that', 'pointer', 'temp')
        assert isinstance(index, int) and index >= 0

        self.asm_file.write(f"// {command} {segment} {index}\n")

        if command == 'push':
            if segment == 'constant':
                asm_store_target_to_D = (f"@{index}", "D=A")
            else:
                asm_set_target_address = self.__get_asm_set_target_address(segment, index)
                asm_store_target_to_D = list(asm_set_target_address) + ["D=M"]
            asm = (
                *asm_store_target_to_D,
                # push it to stack
                "@SP",
                "A=M",
                "M=D",
                # increment stack pointer
                "@SP",
                "M=M+1",
            )
        elif command == 'pop':
            assert segment != 'constant'
            asm_set_target_address = self.__get_asm_set_target_address(segment, index)
            asm = (
                # calculate address to pop to, and store in R13
                *asm_set_target_address,
                "D=A",
                "@R13",
                "M=D",
                # pop top of stack to R13
                "@SP",
                "AM=M-1",
                "D=M",
                "@R13",
                "A=M",
                "M=D",
            )
        else:
            raise ValueError(f"Unknown push/pop command: {command}")
        self.asm_file.write("\n".join(asm) + "\n")

    def close(self) -> None:
        self.asm_file.close()

