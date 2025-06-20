from enum import Enum, auto 
#for enumerating some of the tokens we will deal with, auto simplifies this by automatically assigning a unique value to each token 

#enums for a limited version of lua
#just consists of basic loops and operations
class TokenType(Enum):
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    FUNCTION = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    END = auto()
    WHILE = auto()
    DO = auto()
    RETURN = auto()
    LOCAL = auto()
    ASSIGN = auto()   # =
    PLUS = auto()     # +
    MINUS = auto()    # -
    STAR = auto()     # *
    SLASH = auto()    # /
    LPAREN = auto()   # (
    RPAREN = auto()   # )
    COMMA = auto()    # ,
    SEMICOLON = auto()  # ;
    GREATER = auto()  # >
    GREATER_EQUAL = auto()  # >=
    LESS = auto()  # <
    LESS_EQUAL = auto()  # <=
    EQUAL_EQUAL = auto()  # ==
    DOTDOT = auto() #concat
    EOF = auto()

#create a class for token behaviors

class Token:
    #constructor for the token, stores enum type,  value and what line and column it is in
    #if none is give, default to 0
    def __init__(self, type, value=None, line=0, column=0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    #converts the object into a string (in any case that we need it to be treated as a string)
    def __str__(self):
        #if value is not null then return a formatted string of type: value
        if self.value:
            return f"{self.type}: {self.value}"
        #if it does not have a value return the token type
        return f"{self.type}"
    
#create a simple lexer
class Lexer:
    def __init__(self, source):

        #take in the source code, create a token list and notes what line and column it is on
    
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

        #take note of keywords
        self.keywords = {
            "function": TokenType.FUNCTION,
            "if": TokenType.IF,
            "then": TokenType.THEN,
            "else": TokenType.ELSE,
            "end": TokenType.END,
            "while": TokenType.WHILE,
            "do": TokenType.DO,
            "return": TokenType.RETURN,
            "local": TokenType.LOCAL           
        }
        #tokenize the given source code
        self.tokenize()

    def tokenize(self):
        #checks if the tokenizer is at the end of the source code
        while not self.is_at_end():
            #moves forward by getting current as start and scans theh token
            self.start = self.current
            self.scan_token()

        #at the end, specify an End of file by appending a Token EOF at the edge
        self.tokens.append(Token(TokenType.EOF, None, self.line,self.column))

    def is_at_end(self):
        return self.current >= len(self.source)
    
    #advances the progression of the "pointer" in the lexer
    def advance(self):
        #goes to the current char and moves the current pointer forward
        #this stores the char we have at the actual current for processing
        char = self.source[self.current]
        self.current += 1
        self.column += 1

        #return the used char
        return char
    
    #2 peeks to look ahead without "eating" the token early, unlike advance
    
    #peek is for the current character
    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    #peek_next is for the character ahead
    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def match(self, expected):
        
        #checks if it is at the end or does not match the expected token, return false
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        
        #else, move forward and confirm a match on current
        self.current += 1
        self.column += 1
        return True
    
    def add_token(self, type, value = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(
            type,
            #if value is not null return value else return none
            value if value is not None else text,
            #indicates correct position of token
            self.line,
            self.column - (self.current - self.start)
        ))

    #scans the tokens and verifies what character they take
    def scan_token(self):
        char = self.advance()

        if char.isspace():
            #checks to see if the space is a newline, if true move line up
            if char == '\n':
                self.line += 1
                self.column = 1
            return
        
        #checks to see if it is the alphabet or an _
        if char.isalpha() or char == '_':
            #checks to see if the entire thing is an identifier
            self.identifier()
            return

        #checks if it is a digit
        if char.isdigit():
            #confirms if it is a digit
            self.number()
            return
        
        #potential string
        if char == '"' or char == "'":
            #checks if it is actually a string
            self.string(char)
            return
        
        # assess single char tokens
        if char == '=':
            # check for ==
            if self.peek() == '=':
                self.advance()
                self.add_token(TokenType.EQUAL_EQUAL)
            else:
                self.add_token(TokenType.ASSIGN)
        elif char == '>':
            # check for >=
            if self.peek() == '=':
                self.advance()
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
        elif char == '<':
            # Check for <=
            if self.peek() == '=':
                self.advance()
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
        elif char == '+':
            self.add_token(TokenType.PLUS)
        elif char == '-':
            # check for comments
            if self.peek() == '-':
                # comment goes until the end of the line
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                #if it is just one - then its a minus
                self.add_token(TokenType.MINUS)
        
        elif char == '*':
            self.add_token(TokenType.STAR)
        elif char == '/':
            self.add_token(TokenType.SLASH)
        elif char == '(':
            self.add_token(TokenType.LPAREN)
        elif char == ')':
            self.add_token(TokenType.RPAREN)
        elif char == ',':
            self.add_token(TokenType.COMMA)
        elif char == ';':
            self.add_token(TokenType.SEMICOLON)
        elif char == '.':
            if self.peek() == '.':  # handle .. operator
                self.advance()
                self.add_token(TokenType.DOTDOT)
            else:
                print(f"Unexpected character: {char} at line {self.line}, column {self.column}")
        else:
            # handles unknown chars
            print(f"Unexpected character: {char} at line {self.line}, column {self.column}")

    def identifier(self):
        #checks to see if the next value is alphanumeric, an underscore or is not yet at the end
        while(self.peek().isalnum() or self.peek() == '_') and not self.is_at_end():
            #check further
            self.advance()

        #capture from start to element before current (the entire identifier)
        text = self.source[self.start:self.current]

        type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(type)

    def number(self):
        #check integer part
        while self.peek().isdigit() and not self.is_at_end():
            self.advance()

        #check if there is a . and nums after it (decimal part)
        if self.peek() == '.' and self.peek_next().isdigit():
            #consume the .
            self.advance()

            while self.peek().isdigit() and not self.is_at_end():
                self.advance()

        #same slicing with identifiers
        value = self.source[self.start:self.current]

        #convert automatically
        if '.' in value:
            self.add_token(TokenType.NUMBER, float(value))
        else:
            self.add_token(TokenType.NUMBER, int(value))

    def string(self, quote_char):
        #keep consuming characters until we reach the closing quote

        while self.peek() != quote_char and not self.is_at_end():
            #check for any newlines and move pointer accordingly
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            self.advance()

        #for any unterminated strings
        if self.is_at_end():
            print(f"Unterminated string at line {self.line}")
            return
        
        #consume the closing quote
        self.advance()

        #extract only the string without the quotes

        value = self.source[self.start + 1: self.current-1]
        self.add_token(TokenType.STRING, value)
