from tkinter import *
import tkinter as tk
from counter import Counter

root = Tk()

# main
frame = Frame(root)
frame.pack(fill=BOTH, expand=1)

# canvas
my_canvas = Canvas(frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# ver scrollbar
ver_scrollbar = tk.Scrollbar(frame, orient=VERTICAL, command=my_canvas.yview)
ver_scrollbar.pack(side=RIGHT, fill=Y)


hor_scrollbar = tk.Scrollbar(root, orient=HORIZONTAL, command=my_canvas.xview)
hor_scrollbar.pack(side=BOTTOM, fill=X)

# configure the canvas
my_canvas.configure(yscrollcommand=ver_scrollbar.set, xscrollcommand=hor_scrollbar.set)
my_canvas.bind(
    '<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all"))
)

second_frame = Frame(my_canvas, width = 1000, height = 100)
for i in range(10):
    for j in range(4):
        c = Counter(second_frame, counter_number=i*4+j, font=('B Nazanin', 18))
        c.grid(row=i, column=j)

my_canvas.create_window((0, 0), window=second_frame, anchor="nw")
root.mainloop()