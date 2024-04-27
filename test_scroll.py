from tkinter import *
import tkinter as tk
from tkinter import ttk
from counter import Counter

class Part:
    def __init__(self, root):
        self.root=root
        self.frame1 = Frame(self.root, width=800, height=400)

        self.frame = Frame(self.frame1)
        self.frame.pack(fill=BOTH, expand=1)

        # canvas
        self.my_canvas = Canvas(self.frame)
        self.my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

        # ver scrollbar
        self.ver_scrollbar = tk.Scrollbar(self.frame, orient=VERTICAL, command=self.my_canvas.yview)
        self.ver_scrollbar.pack(side=RIGHT, fill=Y)


        self.hor_scrollbar = tk.Scrollbar(self.frame1, orient=HORIZONTAL, command=self.my_canvas.xview)
        self.hor_scrollbar.pack(side=BOTTOM, fill=X)

        # configure the canvas
        self.my_canvas.configure(yscrollcommand=self.ver_scrollbar.set, xscrollcommand=self.hor_scrollbar.set)
        self.my_canvas.bind('<Configure>', lambda e: self.my_canvas.configure(scrollregion=self.my_canvas.bbox("all")))

        self.second_frame = Frame(self.my_canvas, width = 1000, height = 100)
        for i in range(10):
            for j in range(4):
                c = Counter(self.second_frame, name=i*4+j, font=('B Nazanin', 18))
                c.grid(row=i, column=4-j)

        self.my_canvas.create_window((0, 0), window=self.second_frame, anchor="nw")

    def grid(self, *args, **kwargs):
        self.frame1.grid(*args, **kwargs)

    def place(self, *args, **kwargs):
        self.frame1.place(*args, **kwargs)


staff_window = Tk()
tab_bar_staff_window = ttk.Notebook(staff_window)
tabs_list = []
parts=[]
for i in range(10):
    tabs_list.append(ttk.Frame(tab_bar_staff_window))
    tabs_list[i].pack()
    tab_bar_staff_window.add(tabs_list[i], text =f'بخش {i+1}')
    parts.append(Part(tabs_list[i]))
    parts[i].grid(row=1, column=1)
    # parts[i].place(width=1024, height=400)
tab_bar_staff_window.grid()
staff_window.geometry('1024x400')
staff_window.mainloop()