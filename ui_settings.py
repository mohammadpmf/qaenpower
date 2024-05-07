from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msb


BG='#333333'
BG_LIGHTER='#555555'
FG='orange'
FG2='green'
DISABLED_BG="#777777"
FONT = ('B Nazanin', 24)
FONT2 = ('B Nazanin', 18)
FONT3 = ('B Nazanin', 12)
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
    'selectbackground': FG,
    'selectforeground': BG,
    'font': FONT,
    'insertbackground': FG,
    'readonlybackground': DISABLED_BG,
    'disabledbackground': DISABLED_BG,
}
CNF_ENTRY_USER = CNF_ENTRY.copy()
CNF_ENTRY_COUNTER = CNF_ENTRY_USER.copy()
CNF_ENTRY_COUNTER['width']=WORDS_WIDTH

CNF_GRID = {
    'padx': PADX,
    'pady': PADY+5,
}

CNF_PACK = {
    'side': RIGHT,
    'expand': True,
    'padx': PADX+10,
    'pady': PADY+10,
}


def create_my_theme():
    style = ttk.Style()
    style.theme_use('clam')
    style.theme_create(f'my_style', parent='alt',
                    settings = {
                        'TCombobox': {
                            'configure': {
                                'selectbackground': BG,
                                'fieldbackground': BG,
                                'background': BG,
                                'foreground': FG,
                                }
                            },
                        'TNotebook': {
                            'configure': {
                                'tabmargins': [2, 5, 2, 0], # LTBR
                                'tabposition': 'ne',
                                'background': BG_LIGHTER,
                            }
                        },
                        'TNotebook.Tab': {
                            'configure': {
                                'padding': [5, 1],
                                'background': BG,
                                'foreground': FG,
                                }
                        }
                    })
    style.theme_use(f'my_style')
    style.map('TCombobox', fieldbackground=[('readonly', BG)])
    style.map('TCombobox', selectbackground=[('readonly', BG)])
    style.map('TCombobox', selectforeground=[('readonly',  FG)])
    style.configure("Treeview",background=BG,foreground=FG,rowheight=48,fieldbackground=BG, font=FONT)
    style.configure("Treeview.Heading", background="#222222", foreground=FG2, font=FONT)
    style.map("Treeview",background=[('selected', FG)])
    style.map("Treeview",foreground=[('selected', BG)])
    style.map("TNotebook",background=[('selected', BG)])
    style.map("TNotebook",expand=[('selected', [1, 1, 1, 0])])
