#simple syntax tree to aid in parsing
# Current CFG for a simplified Lua

'''<program> ::= <block>

<block> ::= <statement>*

<statement> ::= <if_stmt>
              | <while_stmt>
              | <func_def>
              | <return_stmt>
              | <assignment>
              | <expr_stmt>

<if_stmt> ::= "if" <expr> "then" <block> ["else" <block>] "end"

<while_stmt> ::= "while" <expr> "do" <block> "end"

<func_def> ::= "function" <IDENTIFIER> "(" [<params>] ")" <block> "end"

<return_stmt> ::= "return" [<expr>]

<assignment> ::= ["local"] <IDENTIFIER> "=" <expr>

<expr_stmt> ::= <expr>

<expr> ::= <comparison>

<comparison> ::= <additive> (("==" | ">" | ">=" | "<" | "<=") <additive>)*

<additive> ::= <multiplicative> (("+" | "-") <multiplicative>)*

<multiplicative> ::= <primary> (("*" | "/") <primary>)*

<primary> ::= <NUMBER>
           | <STRING>
           | <IDENTIFIER>
           | <IDENTIFIER> "(" [<arguments>] ")"
           | "(" <expr> ")"

<params> ::= <IDENTIFIER> ("," <IDENTIFIER>)*

<arguments> ::= <expr> ("," <expr>)* '''

class Node:
    #parent class for any node
    def __int__(self):
        #we dont need to do anything for the base class
        pass
    def __str___(self):
        #returns the name of the subclass
        return self.__class__.__name__
    
class NumberNode(Node):
    #represents a number
    def __init__(self,value):
        #create a node and give it its value
        super().__init__()
        self.value = value

    def __str__(self):
        return f"Number({self.value})"
    
class StringNode(Node):
    #represents a literal strin
    def __init__(self,value):
        #create a node and give it its value
        super().__init__()
        self.value = value

    def __str__(self):
        return f"String({self.value})"

class VariableNode(Node):
    #represents a reference to a variable
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def __str__(self):
        return f"Variable({self.name})"

class BinaryOpNode(Node):
    #represents any operation that needs 2 operands
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right
    
    def __str__(self):
        return f"BinaryOp({self.left}, {self.op.type.name}, {self.right})"
    
class AssignmentNode(Node):
    #represents any assignment
    def __init__(self, variable, value):
        super().__init__()
        self.variable = variable
        self.value = value
    
    def __str__(self):
        return f"Assignment({self.variable}, {self.value})"
    
class IfNode(Node):
    #represents any if statemnt
    def __init__(self, condition, then_branch, else_branch=None):
        super().__init__()
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def __str__(self):
        #if else branch exists, format it else ignore
        if self.else_branch:
            else_str = f", Else={self.else_branch}"
        else:
            else_str = ""        
        return f"If(Condition={self.condition}, Then={self.then_branch}{else_str})"    

class WhileNode(Node):
    #represents a while loop
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body

    def __str__(self):
        return f"While(Condition={self.condition}, Body={self.body})"
    
class FunctionNode(Node):
    #represents a function definition only
    def __init__(self, name, params, body):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body
    
    def __str__(self):
        return f"Function(Name={self.name}, Params={self.params}, Body={self.body})"
    
class FunctionCallNode(Node):
    #represents any function call
    def __init__(self, name, arguments):
        super().__init__()
        self.name = name
        self.arguments = arguments
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.arguments)  #convert arguments into strings
        return f"FunctionCall(Name={self.name}, Args=[{args_str}])"

class ReturnNode(Node):
    #represents a return statement
    def __init__(self, value=None):
        super().__init__()
        self.value = value
    
    def __str__(self):
        return f"Return({self.value})"
    
class BlockNode(Node):
    #represents a block of statements
    def __init__(self, statements):
        super().__init__()
        self.statements = statements
    
    def __str__(self):
        #join each string with a \n
        stmt_strings = [str(stmt) for stmt in self.statements]  # Convert all statements to strings
        stmts = "\n  ".join(stmt_strings)
        return f"Block:\n  {stmts}"