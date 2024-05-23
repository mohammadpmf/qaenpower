from tkinter import Tk, Label, Entry, Button, BooleanVar, Checkbutton, Toplevel, Frame, StringVar, LabelFrame, Canvas, Scrollbar
from tkinter import TOP, RIGHT, LEFT, END, VERTICAL, HORIZONTAL
from tkinter import ttk
from tkinter import messagebox as msb


BG='sky blue'
BG_LIGHTER='sky blue'
FG='black'
FG2='green'
DISABLED_FG = "#aaaaaa"
DISABLED_BG = '#cccccc'
WARNING_COLOR = '#d6d051'
ALARM_COLOR = '#aa0000'
COPY_ICON_SIZE = 25
DATE_PICKER_ICON_SIZE = CHANGE_DAY_ICON_SIZE = 64
SAVE_ICON_SIZE = UPDATE_ICON_SIZE = 64
PADX = 10
PADY = 5
WORDS_WIDTH=15
WORDS_WIDTH2=12
WORDS_WIDTH3=8
BNT_COPY_WIDTH=1
PARAMETER_WIDGET_WIDTH = WORDS_WIDTH2*2
FONT = ('B Nazanin', 24)
FONT2 = ('B Nazanin', 18)
FONT3 = ('B Nazanin', 12)
FONT4 = ('B Nazanin', 8)
PARAMETER_TYPES = ['کنتور', 'ثابت', 'محاسباتی']
DEFAULT_VALUES = ['مقدار کنتور روز قبل', '0', 'خالی']
DEFAULT_DATE_VALUES = ['روز قبل', 'روز جاری', 'روز بعد']

CNF_LBL_FRM = {
    'bg': BG,
    'font': FONT3,
    'padx': PADX,
    'pady': PADY,
}
CNF_FRM = {
    'bg': BG,
}
CNF_BTN = {
    'bg': BG,
    'fg': FG,
    'font': FONT,
    'padx': PADX,
    'pady': PADY,
}
CNF_BTN2 = CNF_BTN.copy()
CNF_BTN2.update({
    'bg': BG_LIGHTER,
    'font': FONT3,
})
CNF_LABEL=CNF_BTN.copy()
CNF_LABEL2=CNF_LABEL.copy()
CNF_LABEL2.update({
    'font': FONT3,
    'disabledforeground': DISABLED_FG,
    'justify': 'c',
})
CNF_CHB=CNF_BTN.copy()
CNF_CHB2=CNF_BTN.copy()
CNF_CHB2['font']=FONT3
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
CNF_ENTRY2 = CNF_ENTRY.copy()
CNF_ENTRY2.update({
    'font': FONT3,
    'justify': 'c',
    'width': WORDS_WIDTH2+WORDS_WIDTH3,
})
CNF_ENTRY_USER = CNF_ENTRY.copy()
CNF_ENTRY_COUNTER = CNF_ENTRY_USER.copy()
CNF_ENTRY_COUNTER['width']=WORDS_WIDTH

CNF_GRID = {
    'padx': PADX,
    'pady': PADY+5,
}
CNF_GRID2={
    'padx': 4,
    'pady': 2,
    'sticky': 'news',
}
CNF_PACK = {
    'side': RIGHT,
    'expand': True,
    'padx': PADX+10,
    'pady': PADY+10,
}
CNF_PACK2 = {
    'side': RIGHT,
    'padx': PADX,
    'pady': PADY,
}
MONTH_NAMES = {
    1: 'فروردین',
    2: 'اردیبهشت',
    3: 'خرداد',
    4: 'تیر',
    5: 'مرداد',
    6: 'شهریور',
    7: 'مهر',
    8: 'آبان',
    9: 'آذر',
    10: 'دی',
    11: 'بهمن',
    12: 'اسفند',
}
WEEKDAYS = {
    0: 'شنبه',
    1: 'یکشنبه',
    2: 'دوشنبه',
    3: 'سه شنبه',
    4: 'چهارشنبه',
    5: 'پنجشنبه',
    6: 'جمعه',
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
                                'tabmargins': [2, 0, 2, 0], # LTBR
                                'tabposition': 'ne',
                                'background': BG,
                            }
                        },
                        'TNotebook.Tab': {
                            'configure': {
                                'padding': [5, 1],
                                'background': BG,
                                'foreground': FG,
                                'font': FONT2
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
    style.map("TNotebook.Tab",background=[('selected', FG)])
    style.map("TNotebook.Tab",foreground=[('selected', BG)])
