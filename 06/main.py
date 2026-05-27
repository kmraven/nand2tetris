import sys
import os
from Parser import Parser, InstructionType
from Code import Code
from SymbolTable import SymbolTable


def main(asm_filepath: str) -> None:    
    with open(asm_filepath, 'r') as asm_file, open(os.path.splitext(asm_filepath)[0] + '.hack', 'w') as hack_file:
        parser = Parser(asm_file=asm_file)
        symbol_table = SymbolTable()

        # First pass: collect labels
        try:
            while True:
                parser.advance()
                if parser.current_instruction_type == InstructionType.L_INSTRUCTION:
                    symbol = parser.symbol()
                    if not symbol_table.contains(symbol):
                        # Specify the next instruction address
                        symbol_table.add_label(symbol, parser.current_address + 1)
        except StopIteration:
            pass

        # Second pass: translate instructions
        parser.reset()
        try:
            while True:
                parser.advance()
                if parser.current_instruction_type == InstructionType.L_INSTRUCTION:
                    continue
                if parser.current_instruction_type == InstructionType.A_INSTRUCTION:
                    symbol = parser.symbol()
                    if symbol.isdigit():
                        number = symbol
                        binary_instruction = f"0{Code.symbol(number)}"
                    else:
                        if not symbol_table.contains(symbol):
                            symbol_table.add_variable(symbol)
                        address = symbol_table.get_address(symbol)
                        binary_instruction = f"0{Code.symbol(address)}"
                elif parser.current_instruction_type == InstructionType.C_INSTRUCTION:
                    dest = parser.dest()
                    comp = parser.comp()
                    jump = parser.jump()
                    binary_instruction = f"111{Code.comp(comp)}{Code.dest(dest)}{Code.jump(jump)}"
                # print(f"Translating instruction: {parser.current_instruction} -> {binary_instruction}")
                hack_file.write(binary_instruction + '\n')
        except StopIteration:
            pass
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <asm_filepath>")
        sys.exit(1)
    asm_filepath = sys.argv[1]
    main(asm_filepath)
