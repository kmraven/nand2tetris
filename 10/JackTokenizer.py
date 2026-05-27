from enum import Enum
from typing import TextIO, Optional
import re
from lexicons import Keyword, SYMBOL


class TokenType(Enum):
    KEYWORD = 'keyword'
    SYMBOL = 'symbol'
    IDENTIFIER = 'identifier'
    INT_CONST = 'integerConstant'
    STRING_CONST = 'stringConstant'


class JackTokenizer:
    def __init__(self, jack_file: TextIO):

        def __strip_empty_lines(code: str) -> str:
            return '\n'.join(line for line in code.splitlines() if line.strip())

        def __strip_comments(code: str) -> str:
            '''
            Removes all comments from the given Jack code.
            1. // ... \n
            2. /* ... */
            '''
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
            code = re.sub(r'//.*?(?=\n|$)', '', code)
            return code
        
        jack_file.seek(0)
        jack_code = __strip_empty_lines(jack_file.read())
        jack_code = __strip_comments(jack_code).replace('\n', ' ')
        self.jack_code_iter = iter(jack_code)
        self.current_token: str = ''
        self.current_token_type: Optional[TokenType] = None
        self.past_token_list: list[str] = []

    def advance(self) -> None:
        if self.current_token:
            self.past_token_list.append(self.current_token)
        self.__get_next_token()
        self.current_token_type = self.token_type()

    def __get_next_token(self) -> None:
        while True:
            char = next(self.jack_code_iter)
            if char.isspace():
                continue
            if char.isdigit():
                while True:
                    next_char = next(self.jack_code_iter)
                    if next_char.isdigit():
                        char += next_char
                        continue
                    elif next_char.isspace() or next_char in SYMBOL:
                        self.current_token = char
                        self.jack_code_iter = iter(next_char + ''.join(self.jack_code_iter))
                        return
                    else:
                        raise ValueError(f'Unexpected character in integer constant: {next_char}')
            if char in SYMBOL:
                self.current_token = char
                return
            if char == '"':
                while True:
                    next_char = next(self.jack_code_iter)
                    char += next_char
                    if next_char == '"':
                        self.current_token = char
                        return
            if char.isalpha() or char == '_':
                while True:
                    next_char = next(self.jack_code_iter)
                    if next_char.isalnum() or next_char == '_':
                        char += next_char
                        continue
                    else:
                        self.current_token = char
                        self.jack_code_iter = iter(next_char + ''.join(self.jack_code_iter))
                        return
            raise ValueError(f'Unexpected character: {char}')

    def backward(self) -> None:
        if not self.past_token_list:
            raise ValueError("No previous token to go back to")
        self.jack_code_iter = iter(self.current_token + ''.join(self.jack_code_iter))
        self.current_token = self.past_token_list.pop()
        self.current_token_type = self.token_type()

    def token_type(self) -> TokenType:
        token = self.current_token
        if token in {kw.value for kw in Keyword}:
            return TokenType.KEYWORD
        elif token in SYMBOL:
            return TokenType.SYMBOL
        elif token.isdigit() and token.isascii() and 0 <= int(token) <= 32767:
            return TokenType.INT_CONST
        elif token.startswith('"') and token.endswith('"'):
            return TokenType.STRING_CONST
        elif all(c.isalnum() or c == '_' for c in token) and (token[0].isalpha() or token[0] == '_'):
            return TokenType.IDENTIFIER
        else:
            raise ValueError(f'{token} : Unknown token type')

    def keyword(self) -> str:
        if self.current_token_type != TokenType.KEYWORD:
            raise ValueError("Current token is not a keyword --- " + self.current_token)
        return Keyword(self.current_token).value

    def symbol(self) -> str:
        if self.current_token_type != TokenType.SYMBOL:
            raise ValueError("Current token is not a symbol --- " + self.current_token)
        return self.current_token
    
    def identifier(self) -> str:
        if self.current_token_type != TokenType.IDENTIFIER:
            raise ValueError("Current token is not an identifier --- " + self.current_token)
        return self.current_token
    
    def int_val(self) -> int:
        if self.current_token_type != TokenType.INT_CONST:
            raise ValueError("Current token is not an integer constant --- " + self.current_token)
        return int(self.current_token)
    
    def string_val(self) -> str:
        if self.current_token_type != TokenType.STRING_CONST:
            raise ValueError("Current token is not a string constant --- " + self.current_token)
        return self.current_token.strip('"')
