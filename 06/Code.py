class Code:
    @staticmethod
    def symbol(symbol: str) -> str:
        if symbol.isdigit():
            return f"{int(symbol):015b}"
        else:
            raise ValueError(f"Symbol must be a digit, got: {symbol}")
    
    @staticmethod
    def dest(mnemonic: str) -> str:
        # check if mnemonic conrains only valid characters
        if not all(c in 'MDAN' for c in mnemonic):
            raise ValueError(f"Invalid dest mnemonic: {mnemonic}")
        is_M = '1' if 'M' in mnemonic else '0'
        is_D = '1' if 'D' in mnemonic else '0'
        is_A = '1' if 'A' in mnemonic else '0'
        return f"{is_A}{is_D}{is_M}"
    
    @staticmethod
    def comp(mnemonic: str) -> str:
        comp_map = {
            '0':   '0101010',
            '1':   '0111111',
            '-1':  '0111010',
            'D':   '0001100',
            'A':   '0110000',
            '!D':  '0001101',
            '!A':  '0110001',
            '-D':  '0001111',
            '-A':  '0110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'D+A': '0000010',
            'D-A': '0010011',
            'A-D': '0000111',
            'D&A': '0000000',
            'D|A': '0010101',
            'M':   '1110000',
            '!M':  '1110001',
            '-M':  '1110011',
            'M+1': '1110111',
            'M-1': '1110010',
            'D+M': '1000010',
            'D-M': '1010011',
            'M-D': '1000111',
            'D&M': '1000000',
            'D|M': '1010101'
        }
        if mnemonic not in comp_map:
            raise ValueError(f"Invalid comp mnemonic: {mnemonic}")
        return comp_map[mnemonic]
    
    @staticmethod
    def jump(mnemonic: str) -> str:
        jump_map = {
            'null': '000',
            'JGT':  '001',
            'JEQ':  '010',
            'JGE':  '011',
            'JLT':  '100',
            'JNE':  '101',
            'JLE':  '110',
            'JMP':  '111'
        }
        if mnemonic not in jump_map:
            raise ValueError(f"Invalid jump mnemonic: {mnemonic}")
        return jump_map[mnemonic]