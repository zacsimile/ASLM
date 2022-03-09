import tkinter as tk
from tkinter import ttk

'''If you need a reference for the types of arguments that different widgets accept you can use the below:
https://tkdocs.com/shipman/
It will help with creating the input_args and label_args dictionaries if you so choose to use them
'''


'''Kwargs can be used to communicate arguments to the parent thru the super init function
To use the kwargs argument:
    treat the kwargs as an array or dict of arguments
    So if you wanted to pass a width and height to the parent you can do so with
    kwargs.update(width=900, height=600) #do it this way to override any values currently there otherwise funky behavior could occur
    super().__init__(parent, **kwargs) # this passes the two arguments above 
'''

'''
User Guide for the Class
If you need reference for default functions in python: https://www.geeksforgeeks.org/default-arguments-in-python/

Lets assume the parent in this case is Settings Frame

LabelInput( settings, 
            label_pos="top",
            label="Exposure Time", 
            input_class=ttk.Spinbox, 
            input_var=tk.IntVar(), 
            input_args={"from_": 0.5, "to": 100, "increment": 0.1},
            label_args={"height": 2, "width": 4}
            )

Please note that these values are arbitrary and just to show usage.

Typically this class will be called as a child of a LabelFrame for a related grouping of data or fields.
Each widget you need to create will be a new instance of the LabelInput class. 

'''



class LabelInput(ttk.Frame):
    '''Widget class that contains label and input together.'''
    #The below takes a parent frame, the postition of the label(left or top defaults to left), type of widget (defaults to entry), the input variable used, input arguments, label arguments and 
    # finally the keyword arguments that will be passed to the super constructor for the frame

    def __init__(self, parent, label_pos="left", label='', input_class=ttk.Entry, input_var=None, input_args=None, label_args=None, **kwargs):
        super().__init__(parent, **kwargs) #Calls frame constructor using parent and keyword args
        input_args = input_args or {} #creating access point to input args for input type constructor (uses these args to create the combobox etc)
        label_args = label_args or {} #same for label args (args to create label etc)
        self.variable = input_var #same for variable of the input, typically this will be a Tk style var like StringVar which can be accessed by any widget in the app
        self.input_class = input_class

        '''This if statement will check for the type of widget being created and will create it based on that, since certain
        widgets need different formatting, like how button types don't need a textvariable like a StringVar()'''
        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            input_args["text"] = label
            input_args["variable"] = input_var
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            input_args["textvariable"] = input_var

        '''This will call the passed in widget types constructor, the **input_args is the dict passed in with the arguments needed for 
        that type if desired, its totally optional'''
        self.widget = input_class(self, **input_args)
        #This if will change the pos of the label based on what is passed in top will put label on top of widge, while left will put it on the left
        if label_pos == "top":
            self.widget.grid(row=1, column=0, sticky=(tk.W + tk.E))
            self.columnconfigure(0, weight=1)
        else:
            self.widget.grid(row=0, column=1, sticky=(tk.W + tk.E))
            self.rowconfigure(0, weight=1)

    
    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        '''
        #### Creating a custom grid function that will default LabelInput.grid() to sticky=tk.W + tk.E
        '''
        super().grid(sticky=sticky, **kwargs)

    
    def get(self):
        '''
        #### Creating a generic get function to catch all types of widgets, this uses the try except block for instances when tkintervariables fails
        '''
        try:
            if self.variable:
                return self.variable.get() #Catches widgets that don't have text
            elif type(self.input) == tk.Text:
                return self.input.get('1.0', tk.END) #This is to account for the different formatting with Text widgets
            else:
                return self.input.get() #Cathces all others like the normal entry widget
        except(TypeError, tk.TclError):
            # Catches times when a numeric entry input has a blank, since this cannot be converted into a numeric value
            return ''
    
    def get_variable(self):
        '''
        # return varaible tied with the widget if any
        '''
        return self.variable

    def set(self, value, *args, **kwargs):
        '''
        #### Creating a generic set funciton to complement the above get
        '''
        if type(self.variable) == tk.BooleanVar:
                self.variable.set(bool(value)) #This will cast the value to bool if the variable is a Tk BooleanVar, bc Boolean.Var().set() can only accept bool type values
        elif self.variable:
                self.variable.set(value, *args, **kwargs) #No casting needed this will set any of the other var types (String, Int, etc)
        elif type(self.input).__name__.endswith('button'): #Catches button style widgets
            #The below if statment is needed for button types because it needs to be selected or enabled based on some value
            if value:
                self.input.select() #If there is a value select the button
            else:
                self.input.deselect() #If there is not deselect it
        elif type(self.input) == tk.Text: #Catches Text type objects so the Multiline Text widget and the Entry widget
            self.input.delete('1.0', tk.END)
            self.input.insert('1.0', value) #These lines are used for the specfic formatting of the Text widget, 1 is the line and 0 is the char pos of that line
        else:
            self.input.delete(0, tk.END)
            self.input.insert(0, value) #Basic entry widget formatting, dont need the string as the first arg

    def set_values(self, values):
        '''
        #### Values should be a list of strings or numbers that you want to be options in the specific widget
        '''

        if self.input_class in (ttk.Combobox, tk.Listbox, ttk.Spinbox):
            self.widget['values'] = values
        else:
            print("This widget class does not support list options: " + self.input_class)
    
    def pad_input(self, left, up, right, down):
        self.widget.grid(padx=(left, right), pady=(up, down))
    

                