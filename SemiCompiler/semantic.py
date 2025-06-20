from lexer import Lexer, TokenType
from parser import Parser
from syntaxtree import (
    NumberNode, StringNode, VariableNode, BinaryOpNode, AssignmentNode,
    IfNode, WhileNode, FunctionNode, FunctionCallNode, ReturnNode, BlockNode
)

class SemanticError(Exception):
    pass

#stores a dictionary of variable and type as well as functions and their parameters
class SymbolTable:
    def __init__(self, parent = None):
        self.variables = {}
        self.functions = {}
        #for consideration in nesting (check parent vars if var is not present in self var)
        self.parent = parent

    def declare_variable(self, name, var_type):
        #declares a variable in the current scope

        if name in self.variables:
            #checks for local duplicates
            raise SemanticError(f"Variable '{name}' is already declared in this scope")
        #add to dictionary 
        self.variables[name] = var_type

    def get_variable(self, name):
        #look up the variable in working scope 
        if name in self.variables:
            return self.variables[name]
        #if parent exists and var was not found in self scope
        #recursively search in parent
        elif self.parent:
            return self.parent.get_variable(name)
        else:
            raise SemanticError(f"Undefined variable '{name}'.")

    #ensures that var_name(params) is fulfilled, return can be void so its None    
    def declare_function(self, name, param_count, param_types, return_type = None):
        #declares a func in current scope
        if name in self.functions:
            raise SemanticError(f"Function '{name}' is already defined.")
        self.functions[name] = (param_count, param_types, return_type)

    def get_function(self, name):
        #same stuff from get_var just for funcs
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        else:
            raise SemanticError(f"Undefined function '{name}'.")

#very basic semantic check, ensures proper func usage and type compatability
class SemanticAnalyzer:
    def __init__(self):
        #create a most parent symbol table (global)
        self.symbol_table = SymbolTable()

        #a current func to verify return types with
        self.current_function = None

        #add in default func (print) in limited lua (print, 1, ["any"], None)
        #-1 means args list in python
        self.symbol_table.declare_function("print", 1, ["any"], None)

    def analyze(self, nodes):
        #analyzes a list of the syntax tree nodes

        #just to make sure singular nodes still get wrapped in a list
        if not isinstance(nodes, list):
            nodes = [nodes]

        #analyze dem
        for node in nodes:
            self.analyze_node(node)

        #if no exceptions raised it returns true
        return True
    
    def analyze_node(self, node):
        #recursively analyze a specific node

        #check type of token first
        if isinstance(node, NumberNode):
            return "number"
        
        elif isinstance(node, StringNode):
            return "string"
        
        elif isinstance(node, VariableNode):
            return self.symbol_table.get_variable(node.name)
        
        #recursively check left and right sides
        elif isinstance(node, BinaryOpNode):
            left_type = self.analyze_node(node.left)
            right_type = self.analyze_node(node.right)

            #check for type of operator
            if node.op.type == TokenType.DOTDOT:
                #concat .. works with any types in Lua (numbers get converted to strings)
                return "string"
            
            #arithmetic operator
            elif node.op.type in [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH]:
                # In Lua, arithmetic operations try to convert strings to numbers
                # So we just return number as the result type
                # BUT we'll add explicit type checking for safety
                if left_type != "number" or right_type != "number":
                    raise SemanticError(
                        f"Cannot perform arithmetic between {left_type} and {right_type} "
                        f"at line {node.op.line}, column {node.op.column}"
                    )
                return "number"
            
            #remaining binary ops are comparisons
            else: 
                # Comparisons work with any types in Lua
                return "boolean"

        #recursively check whether assignments match
        elif isinstance(node, AssignmentNode):
            #determine the type of the expression
            expr_type = self.analyze_node(node.value)

            if isinstance(node.variable, str):  
                var_name = node.variable  # assign directly if it's already a string
            else:
                var_name = node.variable.name  # otherwise, get the name attribute

            #try to check if variable exists, if not declare it
            try: 
                self.symbol_table.get_variable(var_name)
            except SemanticError:
                self.symbol_table.declare_variable(var_name, expr_type)     

            return expr_type      

        #recursively check if expression ends up being boolean
        elif isinstance(node, IfNode):
            condition_type = self.analyze_node(node.condition)
            if condition_type != "boolean":
                raise SemanticError(f"If condition must be boolean, got {condition_type}")
            
            # analyze branches
            self.analyze_node(node.then_branch)
            if node.else_branch:
                self.analyze_node(node.else_branch)

            return None
        
        #same vibes as earlier
        elif isinstance(node, WhileNode):
            condition_type = self.analyze_node(node.condition)
            if condition_type != "boolean":
                raise SemanticError(f"While condition must be boolean, got {condition_type}")
            
            #analyze the body after
            self.analyze_node(node.body)
            return None
        
        elif isinstance(node, FunctionNode):
            #create a new symbol table only for the locally declared vars in the function, keep parent call since it can still acess that
            old_symbol_table = self.symbol_table
            self.symbol_table = SymbolTable(parent = old_symbol_table)

            #save old context of the func and work on current context (for proper returns)
            old_function = self.current_function
            self.current_function = node.name

            param_types = [] 

            #paramters can be of any type
            for param in node.params:
                param_types.append("any")
                #declare them as any
                self.symbol_table.declare_variable(param, "any")
        
            return_type = None

            for stmt in node.body.statements: #body is a block node
                #if node is a returnnode recursively check what type that return is
                if isinstance(stmt, ReturnNode) and stmt.value:
                    #return type now takes that value
                    return_type = self.analyze_node(stmt.value)
            
            #declare the function in parent scope before analyzing body
            old_symbol_table.declare_function(node.name, len(node.params), param_types, return_type)

            #analyze function body with new symbol table
            self.analyze_node(node.body)
            
            #swap current and old symbol tables, sort of like returning control to the calling function
            self.symbol_table = old_symbol_table
            self.current_function = old_function

            return None
        
        elif isinstance(node, FunctionCallNode):
            #get function info from symbol table
            func_info = self.symbol_table.get_function(node.name)
            #get the deets about the func
            param_count, param_types, return_type = func_info

            if len(node.arguments) != param_count:
                #too many or too little arguments
                raise SemanticError(f"Function '{node.name}' expects {param_count} arguments but got {len(node.arguments)}.")
            
            #analyze all arguments (type checking is relaxed like Lua)
            for arg in node.arguments:
                self.analyze_node(arg)
                
            #if return type is not any return it
            return return_type if return_type else "any"
        
        elif isinstance(node, ReturnNode):
            #checks if return is inside the function
            if not self.current_function:
                raise SemanticError("Return statement outside of function.")
            
            if node.value:
                return self.analyze_node(node.value)
            return None
        
        #checks if the block has any semantic errors or has unknown types
        elif isinstance(node, BlockNode):
            old_symbol_table = self.symbol_table
            self.symbol_table = SymbolTable(parent=old_symbol_table)
            
            for stmt in node.statements:
                self.analyze_node(stmt)
            
            self.symbol_table = old_symbol_table
            return None
        
        else:
            raise SemanticError(f"Unknown AST node type: {type(node)}")
        