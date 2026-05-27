from typing import TextIO
from enum import Enum
import xml.etree.ElementTree as ET
from lexicons import Keyword
from JackTokenizer import JackTokenizer, TokenType

DEBUG = False
# DEBUG = True


class ElementType(Enum):
    CLASS = 'class'
    CLASS_VAR_DEC = 'classVarDec'
    SUBROUTINE_DEC = 'subroutineDec'
    PARAMETER_LIST = 'parameterList'
    SUBROUTINE_BODY = 'subroutineBody'
    VAR_DEC = 'varDec'
    STATEMENTS = 'statements'
    LET_STATEMENT = 'letStatement'
    IF_STATEMENT = 'ifStatement'
    WHILE_STATEMENT = 'whileStatement'
    DO_STATEMENT = 'doStatement'
    RETURN_STATEMENT = 'returnStatement'
    EXPRESSION = 'expression'
    TERM = 'term'
    EXPRESSION_LIST = 'expressionList'


class CompilationEngine:
    def __init__(self, jack_filepath: str, xml_filepath: str) -> None:
        with open(jack_filepath, 'r') as jf:
            self.tokenizer = JackTokenizer(jf)
        self.class_name_list: list[str] = []
        class_elem = self.__compile_class()
        # Write to XML file
        tree = ET.ElementTree(class_elem)
        ET.indent(tree, space='  ')
        print(f"Writing XML output to: {xml_filepath}")
        tree.write(xml_filepath, encoding='utf-8', xml_declaration=False, short_empty_elements=False)

    def __compile_class(self) -> ET.Element:
        '''
        'class' className '{' classVarDec* subroutineDec* '}'
        '''
        class_elem = ET.Element(ElementType.CLASS.value)
        self.tokenizer.advance()
        self.__add_keyword(class_elem, Keyword.CLASS.value)
        self.tokenizer.advance()
        self.__add_identifier(class_elem, "class name")
        self.tokenizer.advance()
        self.__add_symbol(class_elem, '{')
        while True:
            self.tokenizer.advance()
            if self.tokenizer.current_token_type == TokenType.KEYWORD and self.tokenizer.keyword() in [Keyword.STATIC.value, Keyword.FIELD.value]:
                self.tokenizer.backward()
                self.__compile_class_var_dec(class_elem)
            else:
                self.tokenizer.backward()
                break
        while True:
            self.tokenizer.advance()
            if self.tokenizer.current_token_type == TokenType.KEYWORD and self.tokenizer.keyword() in [Keyword.CONSTRUCTOR.value, Keyword.FUNCTION.value, Keyword.METHOD.value]:
                self.tokenizer.backward()
                self.__compile_subroutine_dec(class_elem)
            else:
                self.tokenizer.backward()
                break
        self.tokenizer.advance()
        self.__add_symbol(class_elem, '}')
        return class_elem

    def __compile_class_var_dec(self, parent: ET.Element) -> None:
        '''
        ('static' | 'field') type varName (',' varName)* ';'
        '''
        current_elem = ET.SubElement(parent, ElementType.CLASS_VAR_DEC.value)
        self.tokenizer.advance()
        self.__add_keyword(current_elem, [Keyword.STATIC.value, Keyword.FIELD.value])
        self.tokenizer.advance()
        self.__add_type(current_elem, self.__get_type_kw_list())
        self.tokenizer.advance()
        self.__add_identifier(current_elem, "class variable name")
        while True:
            self.tokenizer.advance()
            if self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == ',':
                self.__add_symbol(current_elem, ',')
                self.tokenizer.advance()
                self.__add_identifier(current_elem, "class variable name")
            else:
                break
        self.__add_symbol(current_elem, ';')

    def __compile_subroutine_dec(self, parent: ET.Element) -> None:
        '''
        ('constructor' | 'function' | 'method') ('void' | type) subroutineName parameterList subroutineBody
        '''
        current_elem = ET.SubElement(parent, ElementType.SUBROUTINE_DEC.value)
        self.tokenizer.advance()
        self.__add_keyword(current_elem, [Keyword.CONSTRUCTOR.value, Keyword.FUNCTION.value, Keyword.METHOD.value])
        self.tokenizer.advance()
        self.__add_type(current_elem, [Keyword.VOID.value, *self.__get_type_kw_list()])
        self.tokenizer.advance()
        self.__add_identifier(current_elem, "subroutine name")
        self.__compile_parameter_list(current_elem)
        self.__compile_subroutine_body(current_elem)
    
    def __compile_parameter_list(self, parent: ET.Element) -> None:
        '''
        '(' ( (type varName) (',' type varName)* )? ')'
        '''
        self.tokenizer.advance()
        self.__add_symbol(parent, '(')
        current_elem = ET.SubElement(parent, ElementType.PARAMETER_LIST.value)
        self.tokenizer.advance()
        if self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == ')':
            self.__add_symbol(parent, ')')
        else:
            self.__add_type(current_elem, self.__get_type_kw_list())
            self.tokenizer.advance()
            self.__add_identifier(current_elem, "parameter name")
            while True:
                self.tokenizer.advance()
                if self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == ',':
                    self.__add_symbol(current_elem, ',')
                    self.tokenizer.advance()
                    self.__add_keyword(current_elem, self.__get_type_kw_list())
                    self.tokenizer.advance()
                    self.__add_identifier(current_elem, "parameter name")
                else:
                    break
            self.__add_symbol(parent, ')')

    def __compile_subroutine_body(self, parent: ET.Element) -> None:
        '''
        '{' varDec* statements '}'
        '''
        current_elem = ET.SubElement(parent, ElementType.SUBROUTINE_BODY.value)
        self.tokenizer.advance()
        self.__add_symbol(current_elem, '{')
        while True:
            self.tokenizer.advance()
            if self.tokenizer.current_token_type == TokenType.KEYWORD and self.tokenizer.keyword() == Keyword.VAR.value:
                self.tokenizer.backward()
                self.__compile_var_dec(current_elem)
            else:
                self.tokenizer.backward()
                break
        self.__compile_statements(current_elem)
        self.tokenizer.advance()
        self.__add_symbol(current_elem, '}')
    
    def __compile_var_dec(self, parent: ET.Element) -> None:
        '''
        ( 'var' type varName (',' varName)* ';'
        '''
        current_elem = ET.SubElement(parent, ElementType.VAR_DEC.value)
        self.tokenizer.advance()
        self.__add_keyword(current_elem, Keyword.VAR.value)
        self.tokenizer.advance()
        self.__add_type(current_elem, self.__get_type_kw_list())
        self.tokenizer.advance()
        self.__add_identifier(current_elem, "local variable name")
        while True:
            self.tokenizer.advance()
            if self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == ',':
                self.__add_symbol(current_elem, ',')
                self.tokenizer.advance()
                self.__add_identifier(current_elem, "local variable name")
            else:
                break
        self.__add_symbol(current_elem, ';')
    
    def __compile_statements(self, parent: ET.Element) -> None:
        '''
        statement*
        '''
        current_elem = ET.SubElement(parent, ElementType.STATEMENTS.value)
        while True:
            self.tokenizer.advance()
            if self.tokenizer.current_token_type == TokenType.KEYWORD:
                kw = self.tokenizer.keyword()
                self.tokenizer.backward()
                if kw == Keyword.LET.value:
                    self.__compile_let(current_elem)
                elif kw == Keyword.IF.value:
                    self.__compile_if(current_elem)
                elif kw == Keyword.WHILE.value:
                    self.__compile_while(current_elem)
                elif kw == Keyword.DO.value:
                    self.__compile_do(current_elem)
                elif kw == Keyword.RETURN.value:
                    self.__compile_return(current_elem)
                else:
                    break
            else:
                self.tokenizer.backward()
                break
    
    def __compile_let(self, parent: ET.Element) -> None:
        '''
        'let' varName ('[' expression ']')? '=' expression ';'
        '''
        current_elem = ET.SubElement(parent, ElementType.LET_STATEMENT.value)
        self.tokenizer.advance()
        self.__add_keyword(current_elem, Keyword.LET.value)
        self.tokenizer.advance()
        self.__add_identifier(current_elem, "variable name")
        self.tokenizer.advance()
        if self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == '[':
            self.__add_symbol(current_elem, '[')
            self.__compile_expression(current_elem)
            self.tokenizer.advance()
            self.__add_symbol(current_elem, ']')
            self.tokenizer.advance()
        self.__add_symbol(current_elem, '=')
        self.__compile_expression(current_elem)
        self.tokenizer.advance()
        self.__add_symbol(current_elem, ';')

    def __compile_if(self, parent: ET.Element) -> None:
        '''
        'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?
        '''
        current_elem = ET.SubElement(parent, ElementType.IF_STATEMENT.value)
        self.tokenizer.advance()
        self.__add_keyword(current_elem, Keyword.IF.value)
        self.tokenizer.advance()
        self.__add_symbol(current_elem, '(')
        self.__compile_expression(current_elem)
        self.tokenizer.advance()
        self.__add_symbol(current_elem, ')')
        self.tokenizer.advance()
        self.__add_symbol(current_elem, '{')
        self.__compile_statements(current_elem)
        self.tokenizer.advance()
        self.__add_symbol(current_elem, '}')
        self.tokenizer.advance()
        if self.tokenizer.current_token_type == TokenType.KEYWORD and self.tokenizer.keyword() == Keyword.ELSE.value:
            self.__add_keyword(current_elem, Keyword.ELSE.value)
            self.tokenizer.advance()
            self.__add_symbol(current_elem, '{')
            self.__compile_statements(current_elem)
            self.tokenizer.advance()
            self.__add_symbol(current_elem, '}')
        else:
            self.tokenizer.backward()

    def __compile_while(self, parent: ET.Element) -> None:
        '''
        'while' '(' expression ')' '{' statements '}'
        '''
        current_elem = ET.SubElement(parent, ElementType.WHILE_STATEMENT.value)
        self.tokenizer.advance()
        self.__add_keyword(current_elem, Keyword.WHILE.value)
        self.tokenizer.advance()
        self.__add_symbol(current_elem, '(')
        self.__compile_expression(current_elem)
        self.tokenizer.advance()
        self.__add_symbol(current_elem, ')')
        self.tokenizer.advance()
        self.__add_symbol(current_elem, '{')
        self.__compile_statements(current_elem)
        self.tokenizer.advance()
        self.__add_symbol(current_elem, '}')
    
    def __compile_do(self, parent: ET.Element) -> None:
        '''
        'do' subroutineCall ';'
        '''
        current_elem = ET.SubElement(parent, ElementType.DO_STATEMENT.value)
        self.tokenizer.advance()
        self.__add_keyword(current_elem, Keyword.DO.value)
        self.__compile_subroutine_call(current_elem)
        self.tokenizer.advance()
        self.__add_symbol(current_elem, ';')

    def __compile_return(self, parent: ET.Element) -> None:
        '''
        'return' expression? ';'
        '''
        current_elem = ET.SubElement(parent, ElementType.RETURN_STATEMENT.value)
        self.tokenizer.advance()
        self.__add_keyword(current_elem, Keyword.RETURN.value)
        self.tokenizer.advance()
        if self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == ';':
            self.__add_symbol(current_elem, ';')
        else:
            self.tokenizer.backward()
            self.__compile_expression(current_elem)
            self.tokenizer.advance()
            self.__add_symbol(current_elem, ';')
        

    def __compile_subroutine_call(self, parent: ET.Element) -> None:
        '''
        subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
        '''
        self.tokenizer.advance()
        self.__add_identifier(parent, "subroutine name or class/var name")
        self.tokenizer.advance()
        if self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == '.':
            self.__add_symbol(parent, '.')
            self.tokenizer.advance()
            self.__add_identifier(parent, "subroutine name")
            self.tokenizer.advance()
        self.__add_symbol(parent, '(')
        self.__compile_expression_list(parent)
        self.tokenizer.advance()
        self.__add_symbol(parent, ')')

    def __compile_expression_list(self, parent: ET.Element) -> None:
        '''
        (expression (',' expression)* )?
        '''
        current_elem = ET.SubElement(parent, ElementType.EXPRESSION_LIST.value)
        self.tokenizer.advance()
        if not (self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == ')'):
            self.tokenizer.backward()
            self.__compile_expression(current_elem)
            while True:
                self.tokenizer.advance()
                if self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == ',':
                    self.__add_symbol(current_elem, ',')
                    self.__compile_expression(current_elem)
                else:
                    self.tokenizer.backward()
                    break
        else:
            self.tokenizer.backward()

    def __compile_expression(self, parent: ET.Element) -> None:
        '''
        term (op term)*
        '''
        current_elem = ET.SubElement(parent, ElementType.EXPRESSION.value)
        self.__compile_term(current_elem)
        while True:
            self.tokenizer.advance()
            if self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
                self.__add_symbol(current_elem, self.tokenizer.symbol())
                self.__compile_term(current_elem)
            else:
                self.tokenizer.backward()
                break

    def __compile_term(self, parent: ET.Element) -> None:
        '''
        integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | '(' expression ')' | (unaryOp term) | subroutineCall
        '''
        current_elem = ET.SubElement(parent, ElementType.TERM.value)
        self.tokenizer.advance()
        if self.tokenizer.current_token_type == TokenType.INT_CONST:
            e = ET.SubElement(current_elem, TokenType.INT_CONST.value)
            e.text = f' {self.tokenizer.int_val()} '
        elif self.tokenizer.current_token_type == TokenType.STRING_CONST:
            e = ET.SubElement(current_elem, TokenType.STRING_CONST.value)
            e.text = f' {self.tokenizer.string_val()} '
        elif self.tokenizer.current_token_type == TokenType.KEYWORD and self.tokenizer.keyword() in [Keyword.TRUE.value, Keyword.FALSE.value, Keyword.NULL.value, Keyword.THIS.value]:
            self.__add_keyword(current_elem, [Keyword.TRUE.value, Keyword.FALSE.value, Keyword.NULL.value, Keyword.THIS.value])
        elif self.tokenizer.current_token_type == TokenType.IDENTIFIER:
            self.__add_identifier(current_elem, "variable name or subroutine name or class name")
            self.tokenizer.advance()
            if self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == '[':
                self.__add_symbol(current_elem, '[')
                self.__compile_expression(current_elem)
                self.tokenizer.advance()
                self.__add_symbol(current_elem, ']')
            elif self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() in ['(', '.']:
                if self.tokenizer.symbol() == '.':
                    self.__add_symbol(current_elem, '.')
                    self.tokenizer.advance()
                    self.__add_identifier(current_elem, "subroutine name")
                    self.tokenizer.advance()
                self.__add_symbol(current_elem, '(')
                self.__compile_expression_list(current_elem)
                self.tokenizer.advance()
                self.__add_symbol(current_elem, ')')
            else:
                # variable name only
                self.tokenizer.backward()
        elif self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() == '(':
            self.__add_symbol(current_elem, '(')
            self.__compile_expression(current_elem)
            self.tokenizer.advance()
            self.__add_symbol(current_elem, ')')
        elif self.tokenizer.current_token_type == TokenType.SYMBOL and self.tokenizer.symbol() in ['-', '~']:
            self.__add_symbol(current_elem, self.tokenizer.symbol())
            self.__compile_term(current_elem)
        else:
            raise SyntaxError("Invalid term")

    def __get_type_kw_list(self) -> list[str]:
        return [Keyword.INT.value, Keyword.CHAR.value, Keyword.BOOLEAN.value]

    def __add_type(self, parent: ET.Element, kw_list: list[str]) -> None:
        if self.tokenizer.current_token_type == TokenType.KEYWORD:
            self.__add_keyword(parent, kw_list)
        elif self.tokenizer.current_token_type == TokenType.IDENTIFIER:
            self.__add_identifier(parent, "class name")
            self.class_name_list.append(self.tokenizer.identifier())
        else:
            raise SyntaxError(f"Expected type keyword or class name, but got '{self.tokenizer.current_token_type}'")

    def __add_keyword(self, parent: ET.Element, target_kws: str | list[str]) -> None:
        if self.tokenizer.current_token_type != TokenType.KEYWORD:
            if isinstance(target_kws, list) and self.tokenizer.keyword() not in target_kws:
                raise SyntaxError(f"Expected one of {target_kws} keywords, but got '{self.tokenizer.keyword()}'")
            if isinstance(target_kws, str) and self.tokenizer.keyword() != target_kws:
                raise SyntaxError(f"Expected '{target_kws}' keyword, but got '{self.tokenizer.keyword()}'")
        e = ET.SubElement(parent, TokenType.KEYWORD.value)
        e.text = f' {self.tokenizer.keyword()} '
        if DEBUG: print(self.tokenizer.keyword())
        

    def __add_identifier(self, parent: ET.Element, error_msg_id_role: str) -> None:
        if self.tokenizer.current_token_type != TokenType.IDENTIFIER:
            raise SyntaxError(f"Expected {error_msg_id_role} identifier, but got '{self.tokenizer.current_token_type}'")
        e = ET.SubElement(parent, TokenType.IDENTIFIER.value)
        e.text = f' {self.tokenizer.identifier()} '
        if DEBUG: print(self.tokenizer.identifier())
    
    def __add_symbol(self, parent: ET.Element, target_sym: str) -> None:
        if self.tokenizer.current_token_type != TokenType.SYMBOL or self.tokenizer.symbol() != target_sym:
            raise SyntaxError(f"Expected '{target_sym}' symbol, but got '{self.tokenizer.symbol()}'")
        e = ET.SubElement(parent, TokenType.SYMBOL.value)
        e.text = f' {self.tokenizer.symbol()} '
        if DEBUG: print(self.tokenizer.symbol())
