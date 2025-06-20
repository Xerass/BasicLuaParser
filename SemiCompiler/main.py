import tkinter as tk  
from tkinter import scrolledtext, messagebox  
from lexer import Lexer  
from parser import Parser  
from semantic import SemanticAnalyzer  
from syntaxtree import BlockNode 

class LuaIDE:
    #very very simple ide with tkinter (base gui lib) in python

    def __init__(self, root):
        #initialize the components
        self.root = root
        root.title("Partial Lua Compiler IDE")  #set the title of the window
        root.geometry("800x600")  #set the default window size

        dark_bg = "#1e1e1e"   # Dark gray background
        text_color = "#d4d4d4" # Light gray text
        root.configure(bg=dark_bg)
        
        #create a menu bar at the root
        menubar = tk.Menu(root, bg=dark_bg, fg=text_color)
        filemenu = tk.Menu(menubar, tearoff=0, bg=dark_bg, fg=text_color)
        filemenu.add_command(label="Exit", command=root.quit)  #add an exit option upon 
        menubar.add_cascade(label="File", menu=filemenu)  #attach the file menu
        root.config(menu=menubar)  #add the menubar to the window

        # create the main UI components
        self.create_editor_panel(dark_bg, text_color)
        self.create_output_panel(dark_bg, text_color)

        # add a simple run at the bottom, tell it to run compile upon pressing
        run_button = tk.Button(root, text="Run", command=self.compile_code, height=2, width=10,
                            bg="#28a745", fg="white", activebackground="#218838",
                            font=("Courier", 12, "bold"), relief="ridge", bd=2)
        run_button.pack(pady=10)

        #display the welcome message 
        self.show_welcome_message()

    def create_editor_panel(self, dark_bg, text_color):
        #creates a code editor panel
        editor_frame = tk.Frame(self.root, bg=dark_bg)  # create a container for the editor
        editor_frame.pack(fill=tk.BOTH, expand=True)  # expand to fill the space

        # create a text widget to display line numbers
        self.line_numbers = tk.Text(editor_frame, width=4, padx=5, pady=5,
                                    takefocus=0, border=0, background=dark_bg,
                                    foreground=text_color, state='disabled')  # disable this line to not allow editing them
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)  #move them to the left most side

        # create the main code editor with scroll support
        self.code_editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD,
                                                     undo=True, padx=5, pady=5,
                                                     background=dark_bg, foreground=text_color,
                                                     insertbackground="white",
                                                     selectbackground="#555555", font=("Courier", 12))
        self.code_editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  #fill up remaining space

        #add a key release event to update line numbers when the user types
        self.code_editor.bind("<KeyRelease>", self.update_line_numbers)
        self.update_line_numbers() #initialize some numbers on startup

    def create_output_panel(self, dark_bg, text_color):
        #creates an output panel for displaying verdicts
        output_frame = tk.Frame(self.root, height=150, bg=dark_bg)  #create a frame
        output_frame.pack(fill=tk.BOTH, expand=False)  #add it to the bottom

        #add a label
        tk.Label(output_frame, text="Output", anchor='w', fg=text_color, bg=dark_bg).pack(fill=tk.X)

        #make it scrollable, same as earlier
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, 
                                                    height=8, padx=5, pady=5,
                                                    background=dark_bg, foreground=text_color,
                                                    insertbackground="white",
                                                    selectbackground="#555555", font=("Courier", 12),
                                                    state='disabled')
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    #updates the line nums whenever the user presses a key
    def update_line_numbers(self, event=None):
        # Count the number of lines in the editor by counting each new line instance in the editor
        lines = self.code_editor.get("1.0", tk.END).count('\n') + 1
        #create a string of the numbers
        line_numbers_text = "\n".join(str(i) for i in range(1, lines + 1))

        #update
        self.line_numbers.config(state='normal')  # Enable edits temporarily
        self.line_numbers.delete('1.0', tk.END)  # Clear old numbers
        self.line_numbers.insert('1.0', line_numbers_text)  # Insert new numbers
        self.line_numbers.config(state='disabled')  # Lock it again

    def show_welcome_message(self):
        welcome_msg = """Welcome to the Partial Lua Compiler IDE!

Supported features:
✓ Basic arithmetic: +, -, *, /
✓ Comparisons: >, >=, <, <=, ==
✓ String concatenation with ..
✓ Variables with 'local'
✓ If-then-else-end statements
✓ While loops
✓ Function definitions and calls
✓ Return statements
✓ Single-line comments with --

Example:
local x = 10
if x > 5 then
    print("x is greater than 5")
else
    print("x is 5 or less")
end
"""
        self.output_text.config(state='normal')  #enable writing to output
        self.output_text.insert(tk.END, welcome_msg + "\n")  # Insert welcome text
        self.output_text.config(state='disabled')  # Set back to read-only
        self.output_text.see(tk.END)  #go back to very end of output

    def compile_code(self):
        code = self.code_editor.get("1.0", tk.END).strip()  # Get the code content
        self.clear_output()  # Clear previous output

        if not code:
            self.show_output("No code provided. Please enter some Lua code.")
            return

        self.show_output("Processing your code...\n")

        try:
            lexer = Lexer(code)
            parser = Parser(lexer.tokens)
            ast = parser.parse()
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            self.show_output("\nAll checks passed! Your code is valid in this limited Lua subset.")

        except Exception as e:
            self.show_output(f"\nError encountered during compilation:\n{str(e)}", is_error=True)

    def show_output(self, message, is_error=False):
        self.output_text.config(state='normal')  # Enable writing
        self.output_text.insert(tk.END, message + "\n")  # Insert message
        self.output_text.config(state='disabled') 
        self.output_text.see(tk.END)  #go back to end again

    def clear_output(self):
        self.output_text.config(state='normal')  
        self.output_text.delete('1.0', tk.END)  
        self.output_text.config(state='disabled')

def partialcompiler():
    root = tk.Tk()
    app = LuaIDE(root)
    root.mainloop()

if __name__ == "__main__":
    partialcompiler()
