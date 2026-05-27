import os
from typing import TextIO
from collections import defaultdict


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
        self.file_name: str = ''
        self.current_function: str = ''
        self.symbol_counter: dict[str, int] = defaultdict(int)
        self.return_counter: dict[str, int] = defaultdict(int)
        self.static_counter: int = 0
        self.static_dict: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    
    def set_file_name(self, file_name: str) -> None:
        self.file_name = os.path.splitext(os.path.basename(file_name))[0]

    def write_arithmetic(self, command: str, write_comment: bool = True) -> None:
        assert command in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not')
        if write_comment:
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
            true_label = f"{self.file_name}.IF_TRUE_{self.symbol_counter[self.file_name]}"
            false_label = f"{self.file_name}.IF_FALSE_{self.symbol_counter[self.file_name]}"
            asm = (
                "@SP",
                "AM=M-1",
                "D=M",
                "A=A-1",
                "D=M-D",  # M: left, D: right
                f"@{true_label}",
                f"D;{op}",
                "@SP",
                "A=M-1",
                "M=0",  # False
                f"@{false_label}",
                "0;JMP",
                f"({true_label})",
                "@SP",
                "A=M-1",
                "M=-1",  # True
                f"({false_label})",
            )
            self.symbol_counter[self.file_name] += 1
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
            if index not in self.static_dict[self.file_name].keys():
                self.static_dict[self.file_name][index] = self.static_counter
                self.static_counter += 1
            return (
                f"@{self.static_dict[self.file_name][index] + 16}",
            )
        else:
            raise ValueError(f"Unknown segment: {segment}")

    def write_push_pop(self, command: str, segment: str, index: int, write_comment: bool = True) -> None:
        assert command in ('push', 'pop')
        assert segment in ('argument', 'local', 'static', 'constant', 'this', 'that', 'pointer', 'temp')
        assert isinstance(index, int) and index >= 0

        if write_comment:
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
    
    def write_label(self, label: str, write_comment: bool = True) -> None:
        if write_comment:
            self.asm_file.write(f"// label {label}\n")
        if self.current_function != '':
            label = f"{self.current_function}${label}"
        self.asm_file.write(f"({label})\n")

    def write_goto(self, label: str, write_comment: bool = True) -> None:
        if write_comment:
            self.asm_file.write(f"// goto {label}\n")
        if self.current_function != '':
            label = f"{self.current_function}${label}"
        asm = (
            f"@{label}",
            "0;JMP",
        )
        self.asm_file.write("\n".join(asm) + "\n")

    def write_if(self, label: str, write_comment: bool = True) -> None:
        if write_comment:
            self.asm_file.write(f"// if-goto {label}\n")
        if self.current_function != '':
            label = f"{self.current_function}${label}"
        asm = (
            "@SP",
            "AM=M-1",
            "D=M",
            f"@{label}",
            "D;JNE",
        )
        self.asm_file.write("\n".join(asm) + "\n")

    def write_function(self, function_name: str, n_vars: int, write_comment: bool = True) -> None:
        if write_comment:
            self.asm_file.write(f"// function {function_name} {n_vars}\n")
        self.current_function = function_name
        self.asm_file.write(f"({function_name})\n")
        for _ in range(n_vars):
            self.write_push_pop('push', 'constant', 0, write_comment=False)

    def write_call(self, function_name: str, n_args: int, write_comment: bool = True) -> None:
        if write_comment:
            self.asm_file.write(f"// call {function_name} {n_args}\n")
        asm = (
            # push returnAddress
            f"@{function_name}$ret.{self.return_counter[function_name]}",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            # push LCL
            "@LCL",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            # push ARG
            "@ARG",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            # push THIS
            "@THIS",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            # push THAT
            "@THAT",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            # ARG = SP - 5 - nArgs
            "@SP",
            "D=M",
            "@5",
            "D=D-A",
            f"@{n_args}",
            "D=D-A",
            "@ARG",
            "M=D",
            # LCL = SP
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
            # goto f
            f"@{function_name}",
            "0;JMP",
            # (returnAddress)
            f"({function_name}$ret.{self.return_counter[function_name]})"
        )
        self.asm_file.write("\n".join(asm) + "\n")
        self.return_counter[function_name] += 1


    def write_return(self, write_comment: bool = True) -> None:
        if write_comment:
            self.asm_file.write("// return\n")
        asm = (
            # frame = LCL
            "@LCL",
            "D=M",
            "@R13",
            "M=D",
            # retAddr = *(frame - 5)
            "@5",
            "D=A",
            "@R13",
            "A=M-D",
            "D=M",
            "@R14",
            "M=D",
            # *ARG = pop()
            "@SP",
            "AM=M-1",
            "D=M",
            "@ARG",
            "A=M",
            "M=D",
            # SP = ARG + 1
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D",
            # THAT = *(frame - 1)
            "@1",
            "D=A",
            "@R13",
            "D=M-D",
            "A=D",
            "D=M",
            "@THAT",
            "M=D",
            # THIS = *(frame - 2)
            "@2",
            "D=A",
            "@R13",
            "D=M-D",
            "A=D",
            "D=M",
            "@THIS",
            "M=D",
            # ARG = *(frame - 3)
            "@3",
            "D=A",
            "@R13",
            "D=M-D",
            "A=D",
            "D=M",
            "@ARG",
            "M=D",
            # LCL = *(frame - 4)
            "@4",
            "D=A",
            "@R13",
            "D=M-D",
            "A=D",
            "D=M",
            "@LCL",
            "M=D",
            # goto retAddr
            "@R14",
            "A=M",
            "0;JMP",
        )
        self.asm_file.write("\n".join(asm) + "\n")

    def write_bootstrap(self) -> None:
        asm = (
            "@256",
            "D=A",
            "@SP",
            "M=D",
        )
        self.asm_file.write("\n".join(asm) + "\n")
        self.write_call("Sys.init", 0)

    def close(self) -> None:
        self.asm_file.close()

