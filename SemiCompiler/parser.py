from lexer import TokenType, Token
from syntaxtree import (
    NumberNode, StringNode, VariableNode, BinaryOpNode, AssignmentNode,
    IfNode, WhileNode, FunctionNode, FunctionCallNode, ReturnNode, BlockNode
)

class ParseError(Exception):
    #just to raise errors in any case
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def peek(self):
        #similar to peek from lexer, avoids consumption
        return self.tokens[self.current]
    
    def previous(self):
        #views the previous token
        return self.tokens[self.current - 1]
    
    def is_at_end(self):
        #same as lexer, but checks for EOF instead of input length and current string
        return self.peek().type == TokenType.EOF

    def advance(self):
        #consumes the token
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *types):
        #checks if current token matches a type
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False
    
    def check(self, type):
        #checks if a current token matches an EXACT type
        if self.is_at_end():
            return False
        return self.peek().type == type
    
    def consume(self, type, message):
        #consumes a current token if it is one of the types, else return an error with a message
        if self.check(type):
            return self.advance()
        raise ParseError(f"{message} at line {self.peek().line}, column {self.peek().column}")
   
    def parse(self):    
        #parses the entire token set
        statements = []

        while not self.is_at_end():
            statements.append(self.parse_statement())
        
        return BlockNode(statements) #wrap in a primary block (represents the full program)

    def parse_statement(self):
        #parses token by token (stament by statement)
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.WHILE):
            return self.parse_while_statement()
        elif self.match(TokenType.FUNCTION):
            return self.parse_function_definition()
        elif self.match(TokenType.RETURN):
            return self.parse_return_statement()
        elif self.match(TokenType.LOCAL):
            return self.parse_assignment()
        elif self.check(TokenType.IDENTIFIER) and self.peek_next().type == TokenType.ASSIGN:
            return self.parse_assignment()
        else:
            return self.parse_expression_statement()
        
    def peek_next(self):
        #lookahead token
        #if the next current is equal to or greater thanlength of stream then it must be EOF
        if self.current + 1 >= len(self.tokens):
            return Token(TokenType.EOF)
        return self.tokens[self.current + 1]
    
    def parse_expression_statement(self):
        #parses an expression used as a statment
        expr = self.parse_expression()
        self.match(TokenType.SEMICOLON) #check for the optional semicolons in lua (if ever used)
        return expr
    
    def parse_if_statement(self):
        #parses an if
        condition = self.parse_expression()
        self.consume(TokenType.THEN, "Expected 'then' after if")

        then_branch = BlockNode(self.parse_statement_list([TokenType.ELSE, TokenType.END]))
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = BlockNode(self.parse_statement_list([TokenType.END]))
        self.consume(TokenType.END, "Expected 'end' after if/else block")

        return IfNode(condition, then_branch, else_branch)
    
    def parse_while_statement(self):
        #parses a while
        condition = self.parse_expression()
        self.consume(TokenType.DO, "Expected 'do' after while condition")
        body = BlockNode(self.parse_statement_list([TokenType.END]))
        self.consume(TokenType.END, "Expected 'end' after while body")
        return WhileNode(condition, body)
    
    def parse_function_definition(self):
        #parses a function definition
        name = self.consume(TokenType.IDENTIFIER, "Expected function name")
        self.consume(TokenType.LPAREN, "Expected '(' after function name")
        parameters = []

        #checks for ( and proper identifiers when using ,
        if not self.check(TokenType.RPAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self.match(TokenType.COMMA):
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)

        #checks for ) at end if true check for blocks
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        body = BlockNode(self.parse_statement_list([TokenType.END]))
        self.consume(TokenType.END, "Expected 'end' after function body")
        return FunctionNode(name.value, parameters, body)
    
    def parse_return_statement(self):
        #parses the return
        value = None
        if not self.check(TokenType.END) and not self.check(TokenType.ELSE):
            value = self.parse_expression()
        self.match(TokenType.SEMICOLON)  #check again for optional semicolon
        return ReturnNode(value)
    
    def parse_assignment(self):
        #parses an assignment
        name = None

        #checks for any 'local' keywords 
        if self.previous().type == TokenType.LOCAL:
            name = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'local'").value
        else:
            name = self.advance().value
        
        self.consume(TokenType.ASSIGN, "Expected '=' after variable name")
        value = self.parse_expression()
        self.match(TokenType.SEMICOLON)  # optional semicolon
        return AssignmentNode(name, value)
    
    def parse_statement_list(self, terminator_tokens):
        #parses a list of statements and whatever keyword should terminate this list
        statements = []
        while not self.is_at_end() and not any(self.check(t) for t in terminator_tokens):
            statements.append(self.parse_statement())
        return statements
    
    def parse_expression(self):
        #parses a comparison expression
        return self.parse_concat()
    
    #cool stack tech, we start with comparison, then cascade down to multiplication
    #why? the stack handles the precedence in this way! since the final call is multiplicative, it will always be the first one to pop out of the list!

    def parse_concat(self):
        #parses string concat
        expr = self.parse_comparison()
        
        while self.match(TokenType.DOTDOT):
            operator = self.previous()
            right = self.parse_comparison()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def parse_comparison(self):
        #parses any of the comparative expressions
        expr = self.parse_additive()
        while self.match(TokenType.EQUAL_EQUAL, TokenType.GREATER, 
                        TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.parse_additive()
            expr = BinaryOpNode(expr, operator, right)
        return expr
    
    def parse_additive(self):
        #parses addition
        expr = self.parse_multiplicative()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.parse_multiplicative()
            expr = BinaryOpNode(expr, operator, right)
        return expr
    
    def parse_multiplicative(self):
        #parses multiplicative expressions
        expr = self.parse_primary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.parse_primary()
            expr = BinaryOpNode(expr, operator, right)
        return expr
    
    #final stage of the stack calls for expr, checks for actual literals like strings and nums
    def parse_primary(self):
        #parses literals, variables, groupings, func calls
        # check if the token is a number
        if self.match(TokenType.NUMBER):
            return NumberNode(self.previous().value)
        
        # check if the token is a string
        if self.match(TokenType.STRING):
            return StringNode(self.previous().value)
        
        # check if the token is an identifier (could be a variable or function name)
        if self.match(TokenType.IDENTIFIER):
            name = self.previous().value  # store the identifier's name
            
            # if it's followed by ( its a function call
            if self.match(TokenType.LPAREN):
                arguments = self.parse_arguments()  # parse function arguments
                self.consume(TokenType.RPAREN, "Expected ')' after function arguments")  # ensure closing parenthesis
                return FunctionCallNode(name, arguments)  # return a function call node
            
            # otherwise it's just a variable
            return VariableNode(name)
        
        # check if the token is ( meaning its a grouped expression
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()  # parse whatever is inside the parentheses
            self.consume(TokenType.RPAREN, "Expected ')' after expression")  # ensure closing parenthesis
            return expr  # return the inner expression
        
        # if none of the above matched, raise a parsing error
        raise ParseError(f"Unexpected token: {self.peek()} at line {self.peek().line}")
    
    def parse_arguments(self):
        #parses function calls and their arguments
        arguments = []
        if not self.check(TokenType.RPAREN):
            arguments.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                arguments.append(self.parse_expression())
        return arguments

