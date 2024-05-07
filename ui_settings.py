from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msb


BG='#333333'
FG='orange'
FG2='green'
DISABLED_BG="#777777"
FONT = ('B Nazanin', 24)
PADX = 10
PADY = 5
WORDS_WIDTH=15
COUNTER_TYPES = ['کنتور', 'ثابت', 'محاسباتی']
DEFAULT_VALUES = ['مقدار کنتور روز قبل', '0', 'خالی']
CNF_BTN = {
    'bg': BG,
    'fg': FG,
    'font': FONT,
    'padx': PADX,
    'pady': PADY,
}
CNF_LABEL=CNF_BTN.copy()
CNF_CHB=CNF_BTN.copy()
CNF_ENTRY = {
    'bg': BG,
    'fg': FG,
    'font': FONT,
    'insertbackground': FG,
    'readonlybackground': DISABLED_BG,
}
CNF_ENTRY_USER = CNF_ENTRY.copy()
CNF_ENTRY_COUNTER = CNF_ENTRY_USER.copy()
CNF_ENTRY_COUNTER['width']=WORDS_WIDTH

CNF_GRID = {
    'padx': PADX,
    'pady': PADY+5,
}
