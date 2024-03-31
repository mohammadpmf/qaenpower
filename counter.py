from tkinter import *
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
    def __init__(self, root=Tk, counter_number=1):
        self.root = root
        self.counter_number = counter_number
        self.frame = Frame(self.root, bg='light green')
        self.label = Label(self.frame, text=f"کنتور {self.counter_number}", bg='light green')
        self.entry_input = Entry(self.frame, bg='light green')
        self.entry_output = Entry(self.frame, bg='light green')
        self.btn_copy = Button(self.frame, text='copy', bg='darkcyan')
        self.frame_result = Frame(self.frame, bg='white', padx=16, pady=8)
        self.state = Label(self.frame_result, text='سالم')
        self.smiley = Label(self.frame_result, text='☺', bg='green')
        self.label.grid(row=1, column=3)
        self.entry_input.grid(row=1, column=2)
        self.entry_output.grid(row=1, column=1)
        self.btn_copy.grid(row=2, column=2)
        self.frame_result.grid(row=2, column=1)
        self.state.grid(row=1, column=1)
        self.smiley.grid(row=1, column=2)

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)


if __name__ == "__main__":
    root = Tk()
    root.geometry('1000x800')
    root.title('ثبت کنتور')
    c1 = Counter(root=root)
    c1.grid()
    c1 = Counter(root=root, counter_number=2).grid(row=2, column=1)
    c2 = Counter(root=root, counter_number=3).grid(row=3, column=1)
    c3 = Counter(root=root, counter_number=4).grid(row=4, column=1)
    c4 = Counter(root=root, counter_number=50).grid(row=4, column=2)
    root.mainloop()