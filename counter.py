from tkinter import *

BG  = 'light green'
BG2 = 'darkcyan'
BG3 = 'green'
CNF_ENTRY = {
    'bg': BG,
    'readonlybackground': 'gray',
    'disabledbackground': 'gray',
    'font': ('B Nazanin', 24),
}
CNF_CHB = {
    'bg': BG,
    'font': ('B Nazanin', 24),
}
CNF_BTN = {
    'bg': BG2,
    'font': ('B Nazanin', 24),
}
CNF_LBL = {
    'bg': BG,
    'font': ('B Nazanin', 24),
}
CNF_GRID={
    'padx': 4,
    'pady': 2,
    'sticky': 'e',
}
# class Counter(Button):
#     def __init__(self, *args, root=Tk, **kwargs):
#         Button.__init__(self, *args, **kwargs)
#         self.root = root
#         self.frame = Frame(self.root)
#         self.label = Label(self.frame)
#         self.entry_input = Entry(self.frame)
#         self.entry_output = Entry(self.frame)
#         self.btn_copy = Button(self.frame)
#         self.frame_result = Frame(self.frame)
#         self.state = Label(self.frame_result)
#         self.smiley = Label(self.frame_result)
#         self.label.grid(row=1, column=1)
#         self.entry_input.grid(row=1, column=1)
#         self.entry_output.grid(row=1, column=1)
#         self.btn_copy.grid(row=1, column=1)
#         self.frame_result.grid(row=1, column=1)
#         self.state.grid(row=1, column=1)
#         self.smiley.grid(row=1, column=1)
#         self.frame.grid(row=1, column=1)

class Counter():
    def __init__(self, root=Tk, counter_number=1, *args, **kwargs):
        self.root = root
        self.counter_number = counter_number
        self.frame = Frame(self.root, bg=BG)
        self.label = Label(self.frame, text=f"کنتور {self.counter_number}", bg=BG, *args, **kwargs)
        self.entry_input = Entry(self.frame, bg=BG, *args, **kwargs)
        self.entry_output = Entry(self.frame, bg=BG, *args, **kwargs)
        self.btn_copy = Button(self.frame, text='copy', bg=BG2, *args, **kwargs)
        self.frame_result = Frame(self.frame, bg='white', padx=16, pady=8)
        self.state = Label(self.frame_result, text='سالم', *args, **kwargs)
        self.smiley = Label(self.frame_result, text='☺', bg=BG3, *args, **kwargs)
        self.label.grid(row=1, column=3)
        self.entry_input.grid(row=1, column=2)
        self.entry_output.grid(row=1, column=1)
        self.btn_copy.grid(row=2, column=2)
        self.frame_result.grid(row=2, column=1)
        self.state.grid(row=1, column=1)
        self.smiley.grid(row=1, column=2)

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

class Counter():
    def __init__(self, root=Tk, name='', type_='counter', unit='', default='', variable_name='',
                 warning_lower_bound='', warning_upper_bound='', alarm_lower_bound='', alarm_upper_bound='',
                 formula='', *args, **kwargs):
        self.root = root
        self.name = name
        self.type_ = type_          # counter                   -   fixed                -  calculating
        self.unit = unit
        self.default = default      # previous day number       -   fixed (like 0)       -  None
        self.variable_name = variable_name
        self.warning_lower_bound = warning_lower_bound      # if not in range => bg yellow
        self.warning_upper_bound = warning_upper_bound      # if not in range => bg yellow
        self.alarm_lower_bound = alarm_lower_bound          # if not in range => bg red
        self.alarm_upper_bound = alarm_upper_bound          # if not in range => bg red
        self.formula = formula
        self.frame = Frame(self.root, bg=BG)
        self.label = Label(self.frame, text=f"کنتور {self.name}", cnf=CNF_LBL, *args, **kwargs)
        if self.type_=='fixed':
            pass
        elif self.type_=='calculating':
            pass
        elif self.type_=='counter':
            self.btn_copy = Button(self.frame, text='کپی', cnf=CNF_BTN, command=self.copy_down)
            self.entry_current_counter = Entry(self.frame, cnf=CNF_ENTRY)
            self.entry_previous_counter = Entry(self.frame, cnf=CNF_ENTRY)
            self.entry_workout = Entry(self.frame, cnf=CNF_ENTRY, state='readonly')
            self.boolean_var_bad = BooleanVar(self.frame)
            self.checkbutton_bad = Checkbutton(self.frame, cnf=CNF_CHB, variable=self.boolean_var_bad, text='خرابی کنتور', command=self.check)

            self.label.grid(row=1, column=1, columnspan=3, cnf=CNF_GRID)
            self.btn_copy.grid(row=1, column=3, cnf=CNF_GRID)
            self.entry_workout.grid(row=2, column=1, cnf=CNF_GRID)
            self.entry_current_counter.grid(row=2, column=2, columnspan=2, cnf=CNF_GRID)
            self.checkbutton_bad.grid(row=3, column=1, cnf=CNF_GRID)
            self.entry_previous_counter.grid(row=3, column=2, columnspan=2, cnf=CNF_GRID)
    
    def copy_down(self):
        self.boolean_var_bad.set(False)
        self.check()
        self.entry_current_counter.delete(0, END)
        self.entry_current_counter.insert(0, self.entry_previous_counter.get())
    
    def check(self):
        if self.boolean_var_bad.get():
            self.entry_workout.config(state='normal')
            self.entry_current_counter.config(state='readonly')
            self.entry_previous_counter.config(state='readonly')
        else:
            self.entry_workout.config(state='readonly')
            self.entry_current_counter.config(state='normal')
            self.entry_previous_counter.config(state='normal')


    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)


if __name__ == "__main__":
    root = Tk()
    root.geometry('1000x800')
    root.title('ثبت کنتور')
    c1 = Counter(root=root)
    c1.grid()
    c1 = Counter(root=root, name=2).grid(row=2, column=1)
    c2 = Counter(root=root, name=3).grid(row=3, column=1)
    c3 = Counter(root=root, name=4).grid(row=4, column=1)
    c4 = Counter(root=root, name=50).grid(row=4, column=2)
    root.mainloop()