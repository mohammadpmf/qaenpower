from tkinter import *
import tkinter as tk
from tkinter import ttk
from counter import Counter

WIDTH = 1280
HEIGHT = 720

class Part:
    def __init__(self, root, places_with_counters):
        self.root=root
        self.places_with_counters=places_with_counters # یک لیستی از مکان ها با تعداد کنتورهایی که داخلشون هست.
        # یعنی یک لیستی از تاپل ها که هر کودوم از تاپل ها هر عضوشون یه کنتور هست.

        self.frame1 = Frame(self.root)

        self.frame = Frame(self.frame1)
        self.frame.pack(fill=BOTH, expand=1)

        # canvas
        self.my_canvas = Canvas(self.frame, width=WIDTH*0.96, height=HEIGHT*0.9)
        self.my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

        self.ver_scrollbar = tk.Scrollbar(self.frame, orient=VERTICAL, command=self.my_canvas.yview)
        self.ver_scrollbar.pack(side=RIGHT, fill=Y)

        self.hor_scrollbar = tk.Scrollbar(self.frame1, orient=HORIZONTAL, command=self.my_canvas.xview)
        self.hor_scrollbar.pack(side=BOTTOM, fill=X)

        # configure the canvas
        self.my_canvas.configure(yscrollcommand=self.ver_scrollbar.set, xscrollcommand=self.hor_scrollbar.set)
        self.my_canvas.bind('<Configure>', lambda e: self.my_canvas.configure(scrollregion=self.my_canvas.bbox("all")))

        self.second_frame = Frame(self.my_canvas)
        for i, counters in enumerate(self.places_with_counters):
            for j, counter in enumerate(counters):
                c = Counter(self.second_frame, name=i*4+j, font=('B Nazanin', 18))
                c.grid(row=i, column=1000-j)

        self.my_canvas.create_window((0, 0), window=self.second_frame, anchor="ne")


    def grid(self, *args, **kwargs):
        self.frame1.grid(*args, **kwargs)

    def place(self, *args, **kwargs):
        self.frame1.place(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.frame1.pack(*args, **kwargs)



if __name__ == "__main__":
    staff_window = Tk()
    tab_bar_staff_window = ttk.Notebook(staff_window)
    tabs_list = []
    parts=[]
    for i in range(10):
        tabs_list.append(ttk.Frame(tab_bar_staff_window))
        tabs_list[i].pack()
        tab_bar_staff_window.add(tabs_list[i], text =f'بخش {i+1}')
        parts.append(Part(tabs_list[i], [(1,2,3,4),(1,2), (1,2,3), (1,), (1,2,3,4,5,6)]))
        # parts[i].grid(row=1, column=1)
        parts[i].pack()
        # parts[i].place(width=1024, height=400)
    # tab_bar_staff_window.place(x=200, y=40, width=1000, height=800)
    tab_bar_staff_window.pack(expand=True, fill='both')
    staff_window.geometry(f"{WIDTH}x{HEIGHT}")
    staff_window.mainloop()