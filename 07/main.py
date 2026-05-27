import sys
import os
from Parser import Parser, CommandType
from CodeWriter import CodeWriter

def main(vm_filepath: str) -> None:    
    with open(vm_filepath, 'r') as vm_file, open(os.path.splitext(vm_filepath)[0] + '.asm', 'w') as asm_file:
        parser = Parser(vm_file=vm_file)
        code_writer = CodeWriter(asm_file=asm_file)

        try:
            while True:
                parser.advance()
                if parser.current_command_type == CommandType.C_ARITHMETIC:
                    code_writer.write_arithmetic(parser.arg1())
                if parser.current_command_type in {CommandType.C_POP, CommandType.C_PUSH}:
                    command, arg1 = parser.arg1().split()
                    code_writer.write_push_pop(command, arg1, parser.arg2())
        except StopIteration:
            code_writer.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <vm_filepath>")
        sys.exit(1)
    vm_filepath = sys.argv[1]
    main(vm_filepath)
