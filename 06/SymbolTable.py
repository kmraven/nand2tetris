class SymbolTable:
    def __init__(self):
        self.symbols = {
            "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4,
            "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9,
            "R10": 10, "R11": 11, "R12": 12, "R13": 13,
            "R14": 14, "R15": 15,
            "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
            'SCREEN': 16384, 'KBD': 24576
        }
        self.next_variable_address = 16
    
    def contains(self, symbol: str) -> bool:
        return symbol in self.symbols

    def add_variable(self, symbol: str) -> None:
        if not self.contains(symbol):
            self.symbols[symbol] = self.next_variable_address
            self.next_variable_address += 1

    def add_label(self, symbol: str, address: int) -> None:
        if not self.contains(symbol):
            self.symbols[symbol] = address

    def get_address(self, symbol: str) -> str:
        return str(self.symbols[symbol])