# a simple JSON parser

import sys
import re

token_patterns = [
    ('INTEGER', r'-?\d+'),
    ('FLOAT', r'-?\d+\.\d+'),
    ('STRING', r'"(?:[^"\\]|\\.)*"'),
    ('LCURLY', r'\{'),
    ('RCURLY', r'\}'),
    ('COMMA', r','),
    ('COLON', r':'),
    ('NULL', r'null'),
    ('WHITESPACE', r'\s+')
]

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {repr(self.value)})'

class Lexer:
    def __init__(self, text):
        self.text = text
        self.position = 0
        self.current_token = None

    def get_next_token(self):
        if self.position >= len(self.text):
            return Token('EOF', None)

        for token_type, pattern in token_patterns:
            regex = re.compile(pattern)
            match = regex.match(self.text, self.position)

            if match:
                value = match.group(0)
                token = Token(token_type, value)
                self.position = match.end()
                return token
        
        self.error()

    def error(self):
        raise Exception(f'Invalid character: {self.text[self.position]}')

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    # consume a token 
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}")

    # parse object of the form { "k": "v" }
    def parse_object(self):
        self.eat('LCURLY')
        result = {}

        # empty object
        if self.current_token.type == 'RCURLY':
            self.eat('RCURLY')
            return result
        
        while True: # repeat until no more key value pairs or right curly brace
            key = self.current_token.value[1:-1] # remove quotes
            self.eat('STRING')
            self.eat('COLON')
            value = self.parse_value() # read the value
            result[key] = value
            
            if self.current_token.type == 'RCURLY':
                self.eat('RCURLY')
                break
            self.eat('COMMA')
        
        return result
    
    # parse primitive value (only string and integer implemented)
    def parse_value(self):
        token = self.current_token

        if token.type == 'STRING':
            value = token.value[1:-1]
            self.eat('STRING')
            return value
        elif token.type == 'INTEGER':
            value = int(token.value)
            self.eat('INTEGER')
            return value
        
        self.error(f"Unexpected token type: {token.type}")

    def walk(self):
        self.eat('LCURLY')
        while self.current_token.type != 'RCURLY':
            if self.current_token.type == 'COMMA':
                self.eat('COMMA')
            if self.current_token.type == 'EOF':
                self.error("Unmatched curly braces")
            print(self.current_token)
            self.eat(self.current_token.type)
        self.eat('RCURLY')

    def error(self, message):
        raise Exception(f"Parse error: {message}")

if __name__ == "__main__":
    text = ' {"k1":"v1","k2":"v2","id":2}'

    lexer = Lexer(text)
    parser = Parser(lexer)
    try:
        result = parser.parse_object()
        print("Parsed JSON:", result)
    except Exception as e:
        print(f"Error: {e}")