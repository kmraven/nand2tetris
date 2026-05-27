import sys
import os
from Parser import Parser, CommandType
from CodeWriter import CodeWriter
from typing import List

def main(root_dir: str, asm_name: str, vm_files: List[str]) -> None:
    code_writer = CodeWriter(asm_file=open(os.path.join(root_dir, asm_name + '.asm'), 'w'))
    parser_dict = {vm_file: Parser(vm_file=open(os.path.join(root_dir, vm_file), 'r')) for vm_file in vm_files}
    if len(vm_files) > 1:
        code_writer.write_bootstrap()

    for vm_file, parser in parser_dict.items():
        try:
            while True:
                code_writer.set_file_name(vm_file)
                parser.advance()
                if parser.current_command_type == CommandType.C_ARITHMETIC:
                    code_writer.write_arithmetic(parser.arg1())
                elif parser.current_command_type in {CommandType.C_POP, CommandType.C_PUSH}:
                    command, arg1 = parser.arg1().split()
                    code_writer.write_push_pop(command, arg1, parser.arg2())
                elif parser.current_command_type == CommandType.C_LABEL:
                    _, arg1 = parser.arg1().split()
                    code_writer.write_label(arg1)
                elif parser.current_command_type == CommandType.C_GOTO:
                    _, arg1 = parser.arg1().split()
                    code_writer.write_goto(arg1)
                elif parser.current_command_type == CommandType.C_IF:
                    _, arg1 = parser.arg1().split()
                    code_writer.write_if(arg1)
                elif parser.current_command_type == CommandType.C_FUNCTION:
                    _, arg1 = parser.arg1().split()
                    code_writer.write_function(arg1, parser.arg2())
                elif parser.current_command_type == CommandType.C_CALL:
                    _, arg1 = parser.arg1().split()
                    code_writer.write_call(arg1, parser.arg2())
                elif parser.current_command_type == CommandType.C_RETURN:
                    code_writer.write_return()
        except StopIteration:
            pass

    code_writer.close()
    for parser in parser_dict.values():
        parser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <vm_file | vm_directory>")
        sys.exit(1)
    vm_path = sys.argv[1]
    if not os.path.exists(vm_path):
        print(f"Error: The file or directory '{vm_path}' does not exist.")
        sys.exit(1)
    if os.path.isdir(vm_path):
        root_dir = vm_path
        asm_name = os.path.basename(vm_path)
        vm_files = [os.path.basename(f) for f in os.listdir(vm_path) if f.endswith('.vm')]
        if not vm_files:
            print(f"No .vm files found in directory: {vm_path}")
            sys.exit(1)
    else:
        if not vm_path.endswith('.vm'):
            print(f"Error: The file '{vm_path}' is not a .vm file.")
            sys.exit(1)
        root_dir = '.'
        asm_name = os.path.splitext(vm_path)[0]
        vm_files = [vm_path]
    main(root_dir, asm_name, vm_files)
