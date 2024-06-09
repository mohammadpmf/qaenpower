from tkinter import Tk, Label, Entry, Button, BooleanVar, Checkbutton, Toplevel, Frame, StringVar, LabelFrame, Canvas, Scrollbar
from tkinter import TOP, RIGHT, BOTTOM, LEFT, END, VERTICAL, HORIZONTAL
from tkinter import ttk
from tkinter import colorchooser
from tkinter import messagebox as msb
from json import dump, load
from json.decoder import JSONDecodeError


try:
    f = open(r'files/theme.json', 'r')
    COLORS = load(f)
    f.close()
except JSONDecodeError:
    COLORS = {
        "BG": "sky blue",
        "BG_LIGHTER": "sky blue",
        "FG": "black",
        "FG2": "green",
        "DISABLED_FG": "#1b1b1b",
        "DISABLED_BG": "#cccccc",
        "WARNING_COLOR": "yellow",
        "ALARM_COLOR": "red",
        "OK_COLOR": "light green",
    }
except FileNotFoundError:
    COLORS = {
        "BG": "sky blue",
        "BG_LIGHTER": "sky blue",
        "FG": "black",
        "FG2": "green",
        "DISABLED_FG": "#1b1b1b",
        "DISABLED_BG": "#cccccc",
        "WARNING_COLOR": "yellow",
        "ALARM_COLOR": "red",
        "OK_COLOR": "light green",
    }

INVALID_DATE = "!!! تاریخ نامعتبر !!!"
COPY_ICON_SIZE = 25
DATE_PICKER_ICON_SIZE = CHANGE_DAY_ICON_SIZE = 64
SAVE_ICON_SIZE = UPDATE_ICON_SIZE = REFRESH_ICON_SIZE = SETTINGS_ICON_SIZE = 64
PADX = 10
PADY = 5
WORDS_WIDTH=15
WORDS_WIDTH2=12
WORDS_WIDTH3=8
BNT_COPY_WIDTH=1
PARAMETER_WIDGET_WIDTH = WORDS_WIDTH2*2
FONT = ('B Nazanin', 24)
FONT2 = ('B Nazanin', 18)
FONT2_5 = ('B Nazanin', 16)
FONT3 = ('B Nazanin', 12)
FONT4 = ('B Nazanin', 8)
PARAMETER_TYPES = ['کنتور', 'ثابت', 'محاسباتی']
DEFAULT_VALUES = ['مقدار کنتور روز قبل', '0', 'خالی']
DEFAULT_DATE_VALUES = ['روز قبل', 'روز جاری']

CNF_LBL_FRM = {
    'bg': COLORS['BG'],
    'font': FONT3,
    'padx': PADX,
    'pady': PADY,
}
CNF_FRM = {
    'bg': COLORS['BG'],
}
CNF_BTN = {
    'bg': COLORS['BG'],
    'fg': COLORS['FG'],
    'font': FONT,
    'padx': PADX,
    'pady': PADY,
}
CNF_BTN2 = {
    'bg': COLORS['BG_LIGHTER'],
    'fg': COLORS['FG'],
    'font': FONT3,
    'padx': PADX,
    'pady': PADY,
}
CNF_LABEL={
    'bg': COLORS['BG'],
    'fg': COLORS['FG'],
    'font': FONT,
    'padx': PADX,
    'pady': PADY,
}
CNF_LABEL2={
    'bg': COLORS['BG'],
    'fg': COLORS['FG'],
    'font': FONT3,
    'padx': PADX,
    'pady': PADY,
    'disabledforeground': COLORS['DISABLED_FG'],
    'justify': 'c',
}
CNF_LABEL3={
    'bg': COLORS['BG'],
    'fg': COLORS['FG'],
    'font': FONT4,
    'padx': PADX,
    'pady': PADY,
    'disabledforeground': COLORS['DISABLED_FG'],
    'justify': 'c',
}
CNF_CHB={
    'bg': COLORS['BG'],
    'fg': COLORS['FG'],
    'font': FONT,
    'padx': PADX,
    'pady': PADY,
}
CNF_CHB2={
    'bg': COLORS['BG'],
    'fg': COLORS['FG'],
    'font': FONT3,
    'padx': PADX,
    'pady': PADY,
}
CNF_ENTRY = {
    'bg': COLORS['BG'],
    'fg': COLORS['FG'],
    'selectbackground': COLORS['FG'],
    'selectforeground': COLORS['BG'],
    'font': FONT,
    'insertbackground': COLORS['FG'],
    'readonlybackground': COLORS['DISABLED_BG'],
    'disabledbackground': COLORS['DISABLED_BG'],
    'disabledforeground': COLORS['DISABLED_FG'],
}
CNF_ENTRY2 = {
    'bg': COLORS['BG'],
    'fg': COLORS['FG'],
    'selectbackground': COLORS['FG'],
    'selectforeground': COLORS['BG'],
    'font': FONT3,
    'insertbackground': COLORS['FG'],
    'readonlybackground': COLORS['DISABLED_BG'],
    'disabledbackground': COLORS['DISABLED_BG'],
    'disabledforeground': COLORS['DISABLED_FG'],
    'justify': 'c',
    'width': WORDS_WIDTH2+WORDS_WIDTH3,
}
CNF_ENTRY_USER = {
    'bg': COLORS['BG'],
    'fg': COLORS['FG'],
    'selectbackground': COLORS['FG'],
    'selectforeground': COLORS['BG'],
    'font': FONT,
    'insertbackground': COLORS['FG'],
    'readonlybackground': COLORS['DISABLED_BG'],
    'disabledbackground': COLORS['DISABLED_BG'],
    'disabledforeground': COLORS['DISABLED_FG'],
}
CNF_ENTRY_COUNTER = {
    'bg': COLORS['BG'],
    'fg': COLORS['FG'],
    'selectbackground': COLORS['FG'],
    'selectforeground': COLORS['BG'],
    'font': FONT,
    'insertbackground': COLORS['FG'],
    'readonlybackground': COLORS['DISABLED_BG'],
    'disabledbackground': COLORS['DISABLED_BG'],
    'disabledforeground': COLORS['DISABLED_FG'],
    'width': WORDS_WIDTH,
}
CNF_GRID = {
    'padx': PADX,
    'pady': PADY+5,
    'sticky': 'ew'
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
                                'selectbackground': COLORS['BG'],
                                'fieldbackground': COLORS['BG'],
                                'background': COLORS['BG'],
                                'foreground': COLORS['FG'],
                                }
                            },
                        'TNotebook': {
                            'configure': {
                                'tabmargins': [2, 0, 2, 0], # LTBR
                                'tabposition': 'ne',
                                'background': COLORS['BG'],
                            }
                        },
                        'TNotebook.Tab': {
                            'configure': {
                                'padding': [5, 1],
                                'background': COLORS['BG'],
                                'foreground': COLORS['FG'],
                                'font': FONT2
                                }
                        }
                    })
    style.theme_use(f'my_style')
    style.map('TCombobox', fieldbackground=[('readonly', COLORS['BG'])])
    style.map('TCombobox', selectbackground=[('readonly', COLORS['BG'])])
    style.map('TCombobox', selectforeground=[('readonly',  COLORS['FG'])])
    style.configure("Treeview",background=COLORS['BG'],foreground=COLORS['FG'],rowheight=48,fieldbackground=COLORS['BG'], font=FONT)
    style.configure("Treeview.Heading", background="#222222", foreground=COLORS['FG2'], font=FONT)
    style.map("Treeview",background=[('selected', COLORS['FG'])])
    style.map("Treeview",foreground=[('selected', COLORS['BG'])])
    style.map("TNotebook",background=[('selected', COLORS['BG'])])
    style.map("TNotebook",expand=[('selected', [1, 1, 1, 0])])
    style.map("TNotebook.Tab",background=[('selected', COLORS['FG'])])
    style.map("TNotebook.Tab",foreground=[('selected', COLORS['BG'])])
