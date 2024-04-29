from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msb
from connection import Connection

BG='light blue'
FG='orange'
FONT = ('B Nazanin', 24)
PADX = 10
PADY = 5
WORDS_WIDTH=15
COUNTER_TYPES = ['کنتور', 'ثابت', 'محاسباتی']
DEFAULT_VALUES = ['0', 'مقدار کنتور روز قبل', 'خالی']
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
}
CNF_ENTRY_USER = CNF_ENTRY.copy()
CNF_ENTRY_COUNTER = CNF_ENTRY_USER.copy()
CNF_ENTRY_COUNTER['width']=WORDS_WIDTH


CNF_GRID = {
    'padx': PADX,
    'pady': PADY+5,
}

class RegistrationForm():
    def __init__(self, connection: Connection, root:Tk, admin_window:Toplevel, staff_window:Tk):
        self.connection=connection
        self.root = root
        self.admin_window = admin_window
        self.staff_window = staff_window
        self.tab_ontrol = ttk.Notebook(self.admin_window) 
        self.frame_add_part = Frame(self.tab_ontrol, bg=BG) 
        self.frame_add_place = Frame(self.tab_ontrol, bg=BG) 
        self.frame_add_counter = Frame(self.tab_ontrol, bg=BG) 
        self.frame_add_user = Frame(self.tab_ontrol, bg=BG) 
        # self.tab_ontrol.add(ttk.Frame(self.tab_ontrol), text =' '*200) 
        self.tab_ontrol.add(self.frame_add_part, text ='افزودن بخش جدید') 
        self.tab_ontrol.add(self.frame_add_place, text ='افزودن مکان جدید') 
        self.tab_ontrol.add(self.frame_add_counter, text ='افزودن کنتور جدید') 
        self.tab_ontrol.add(self.frame_add_user, text ='افزودن کاربر جدید') 



        # frame_user
        self.frame_user = Frame(self.frame_add_user, bg=BG)
        self.frame_user.grid()
        self.label_name = Label(self.frame_user, text="نام", cnf=CNF_LABEL)
        self.entry_name = Entry(self.frame_user, cnf=CNF_ENTRY_USER, justify='right')
        self.label_surname = Label(self.frame_user, text="نام خانوادگی", cnf=CNF_LABEL)
        self.entry_surname = Entry(self.frame_user, cnf=CNF_ENTRY_USER, justify='right')
        self.label_username = Label(self.frame_user, text="نام کاربری", cnf=CNF_LABEL)
        self.entry_username = Entry(self.frame_user, cnf=CNF_ENTRY_USER)
        self.label_password1 = Label(self.frame_user, text="رمز عبور", cnf=CNF_LABEL)
        self.entry_password1 = Entry(self.frame_user, cnf=CNF_ENTRY_USER, show='*')
        self.label_password2 = Label(self.frame_user, text="تکرار رمز عبور", cnf=CNF_LABEL)
        self.entry_password2 = Entry(self.frame_user, cnf=CNF_ENTRY_USER, show='*')
        self.bv_show_password = BooleanVar(self.frame_user)
        self.checkbox_show_password = Checkbutton(self.frame_user, text='نمایش رمز عبور', variable=self.bv_show_password, cnf=CNF_CHB, command=self.show_password)
        self.btn_register = Button(self.frame_user, text='ایجاد حساب کاربری', cnf=CNF_BTN, command=self.create_account)
        self.btn_back = Button(self.frame_user, text='بازگشت به صفحه ورود', cnf=CNF_BTN, command=self.back)
        self.label_name.grid(row=1, column=3, cnf=CNF_GRID)
        self.entry_name.grid(row=1, column=1, cnf=CNF_GRID)
        self.label_surname.grid(row=3, column=3, cnf=CNF_GRID)
        self.entry_surname.grid(row=3, column=1, cnf=CNF_GRID)
        self.label_username.grid(row=5, column=3, cnf=CNF_GRID)
        self.entry_username.grid(row=5, column=1, cnf=CNF_GRID)
        self.label_password1.grid(row=7, column=3, cnf=CNF_GRID)
        self.entry_password1.grid(row=7, column=1, cnf=CNF_GRID)
        self.label_password2.grid(row=9, column=3, cnf=CNF_GRID)
        self.entry_password2.grid(row=9, column=1, cnf=CNF_GRID)
        self.checkbox_show_password.grid(row=11, column=3, cnf=CNF_GRID)
        self.btn_register.grid(row=13, column=3, cnf=CNF_GRID)
        self.btn_back.grid(row=13, column=1, cnf=CNF_GRID)
        self.entry_name.bind('<Return>', lambda e: self.entry_surname.focus_set())
        self.entry_surname.bind('<Return>', lambda e: self.entry_username.focus_set())
        self.entry_username.bind('<Return>', lambda e: self.entry_password1.focus_set())
        self.entry_password1.bind('<Return>', lambda e: self.entry_password2.focus_set())


        # frame_counter
        self.frame_counter = Frame(self.frame_add_counter, bg=BG)
        self.frame_counter.grid()
        self.label_counter_name = Label(self.frame_counter, text="نام کنتور", cnf=CNF_LABEL)
        self.entry_counter_name = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER, justify='right')
        self.label_counter_type = Label(self.frame_counter, text="نوع کنتور", cnf=CNF_LABEL)
        self.entry_counter_type = ttk.Combobox(self.frame_counter, values=COUNTER_TYPES, font=FONT, width=WORDS_WIDTH, justify='center')
        self.entry_counter_type.insert(0, COUNTER_TYPES[0])
        self.entry_counter_type.config(state='readonly')
        self.entry_counter_type.bind("<<ComboboxSelected>>", self.check_counter_type)
        self.label_unit = Label(self.frame_counter, text="واحد اندازه گیری", cnf=CNF_LABEL)
        self.entry_unit = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.label_default_value = Label(self.frame_counter, text="مقدار پیش فرض", cnf=CNF_LABEL)
        self.entry_default_value = ttk.Combobox(self.frame_counter, values=DEFAULT_VALUES, font=FONT, width=WORDS_WIDTH, justify='center')
        self.entry_default_value.insert(0, DEFAULT_VALUES[0])
        self.entry_default_value.config(state='readonly')
        self.label_variable_name = Label(self.frame_counter, text="نام متغیر", cnf=CNF_LABEL)
        self.entry_variable_name = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.label_warning_lower_bound = Label(self.frame_counter, text="حد پایین هشدار", cnf=CNF_LABEL)
        self.entry_warning_lower_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.label_warning_upper_bound = Label(self.frame_counter, text="حد بالای هشدار", cnf=CNF_LABEL)
        self.entry_warning_upper_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.label_alarm_lower_bound = Label(self.frame_counter, text="حد پایین خطر", cnf=CNF_LABEL)
        self.entry_alarm_lower_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.label_alarm_upper_bound = Label(self.frame_counter, text="حد بالای خطر", cnf=CNF_LABEL)
        self.entry_alarm_upper_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.label_formula = Label(self.frame_counter, text="فرمول", cnf=CNF_LABEL)
        self.entry_formula = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.btn_counter_register = Button(self.frame_counter, text='ایجاد کنتور', cnf=CNF_BTN, command=self.create_counter)
        self.btn_counter_back = Button(self.frame_counter, text='بازگشت به صفحه ورود', cnf=CNF_BTN, command=self.back)
        self.label_counter_name.grid(row=1, column=7, cnf=CNF_GRID)
        self.entry_counter_name.grid(row=1, column=5, cnf=CNF_GRID)
        self.label_counter_type.grid(row=3, column=7, cnf=CNF_GRID)
        self.entry_counter_type.grid(row=3, column=5, cnf=CNF_GRID)
        self.label_unit.grid(row=5, column=7, cnf=CNF_GRID)
        self.entry_unit.grid(row=5, column=5, cnf=CNF_GRID)
        self.label_default_value.grid(row=7, column=7, cnf=CNF_GRID)
        self.entry_default_value.grid(row=7, column=5, cnf=CNF_GRID)
        self.label_variable_name.grid(row=9, column=7, cnf=CNF_GRID)
        self.entry_variable_name.grid(row=9, column=5, cnf=CNF_GRID)
        self.label_warning_lower_bound.grid(row=11, column=7, cnf=CNF_GRID)
        self.entry_warning_lower_bound.grid(row=11, column=5, cnf=CNF_GRID)
        self.label_warning_upper_bound.grid(row=11, column=3, cnf=CNF_GRID)
        self.entry_warning_upper_bound.grid(row=11, column=1, cnf=CNF_GRID)
        self.label_alarm_lower_bound.grid(row=13, column=7, cnf=CNF_GRID)
        self.entry_alarm_lower_bound.grid(row=13, column=5, cnf=CNF_GRID)
        self.label_alarm_upper_bound.grid(row=13, column=3, cnf=CNF_GRID)
        self.entry_alarm_upper_bound.grid(row=13, column=1, cnf=CNF_GRID)
        self.label_formula.grid(row=15, column=7, cnf=CNF_GRID)
        self.entry_formula.grid(row=15, column=5, cnf=CNF_GRID)
        self.btn_counter_register.grid(row=17, column=7, cnf=CNF_GRID)
        self.btn_counter_back.grid(row=17, column=5, cnf=CNF_GRID)
        self.entry_counter_name.bind('<Return>', lambda e: self.entry_counter_type.focus_set())
        self.entry_counter_type.bind('<Return>', lambda e: self.entry_unit.focus_set())
        self.entry_unit.bind('<Return>', lambda e: self.entry_default_value.focus_set())
        self.entry_default_value.bind('<Return>', lambda e: self.entry_variable_name.focus_set())
        self.entry_variable_name.bind('<Return>', lambda e: self.entry_warning_lower_bound.focus_set())
        self.entry_warning_lower_bound.bind('<Return>', lambda e: self.entry_warning_upper_bound.focus_set())
        self.entry_warning_upper_bound.bind('<Return>', lambda e: self.entry_alarm_lower_bound.focus_set())
        self.entry_alarm_lower_bound.bind('<Return>', lambda e: self.entry_alarm_upper_bound.focus_set())
        self.entry_alarm_upper_bound.bind('<Return>', lambda e: exit())


        # frame_part
        self.frame_part = Frame(self.frame_add_part, bg=BG)
        self.frame_part.place(relx=0.4, rely=0.04, relwidth=1, relheight=1)
        self.label_part_name = Label(self.frame_part, text="نام بخش", cnf=CNF_LABEL)
        self.entry_part_name = Entry(self.frame_part, cnf=CNF_ENTRY_COUNTER, justify='right')
        self.btn_part_register = Button(self.frame_part, text='ایجاد بخش', cnf=CNF_BTN, command=self.create_part)
        self.btn_part_back = Button(self.frame_part, text='بازگشت به صفحه ورود', cnf=CNF_BTN, command=self.back)

        self.label_part_name.grid(row=1, column=7, cnf=CNF_GRID)
        self.entry_part_name.grid(row=1, column=5, cnf=CNF_GRID)
        self.btn_part_register.grid(row=17, column=7, cnf=CNF_GRID)
        self.btn_part_back.grid(row=17, column=5, cnf=CNF_GRID)

        # frame_place






    # user functions
    def show_password(self):
        if self.bv_show_password.get():
            self.entry_password1.config(show='')
            self.label_password2.grid_forget()
            self.entry_password2.grid_forget()
            self.entry_password1.focus_set()
        else:
            self.entry_password1.config(show='*')
            self.label_password2.grid(row=9, column=3, cnf=CNF_GRID)
            self.entry_password2.grid(row=9, column=1, cnf=CNF_GRID)
            self.entry_password2.focus_set()

    def create_account(self):
        name = self.entry_name.get()
        surname = self.entry_surname.get()
        username = self.entry_username.get()
        password1 = self.entry_password1.get()
        password2 = self.entry_password2.get()
        if name=="":
            msb.showerror("ارور نام", "نام نمی تواند خالی باشد")
            self.entry_name.focus_set()
            return
        if surname=="":
            msb.showerror("ارور نام خانوادگی", "نام خانوادگی نمی تواند خالی باشد")
            self.entry_surname.focus_set()
            return
        if username=="":
            msb.showerror("ارور نام کاربری", "نام کاربری نمی تواند خالی باشد")
            self.entry_username.focus_set()
            return
        if password1=="":
            msb.showerror("ارور رمز عبور", "رمز عبور نمی تواند خالی باشد")
            self.entry_password1.focus_set()
            return
        if self.bv_show_password.get()==False and password1!=password2:
            msb.showerror("ارور رمز عبور", "رمز عبور ها با یکدیگر مطابقت ندارند")
            self.entry_password2.focus_set()
            return
        result_message, result = self.connection.create_user(name, surname, username, password1)
        if result_message == "ok":
            self.reset()
            msb.showinfo("پیام موفقیت", f"نام کاربری {username} با موفقیت ساخته شد")
        else:
            msb.showerror("ارور", result_message)

    def reset(self):
        self.bv_show_password.set(False)
        self.show_password()
        self.entry_name.delete(0, END)
        self.entry_surname.delete(0, END)
        self.entry_username.delete(0, END)
        self.entry_password1.delete(0, END)
        self.entry_password2.delete(0, END)
        self.entry_name.focus_set()



    # counter functions
    def create_counter(self):
        print('counter created')

    def check_counter_type(self, event=None):
        print(self.entry_counter_type.get())


    # part functions
    def create_part(self):
        print('part created')




    # generic functions
    def back(self):
        self.reset()
        self.root.deiconify()
        self.admin_window.withdraw()

    def grid(self, *args, **kwargs):
        self.tab_ontrol.grid(sticky='e')

class LoginForm():
    def __init__(self, connection: Connection, root:Tk, admin_window:Toplevel, staff_window:Tk):
        self.connection=connection
        self.root = root
        self.admin_window = admin_window
        self.staff_window = staff_window
        self.frame = Frame(self.root, bg=BG)
        self.label_username = Label(self.frame, text="نام کاربری", cnf=CNF_LABEL)
        self.entry_username = Entry(self.frame, cnf=CNF_ENTRY)
        self.label_password = Label(self.frame, text="رمز عبور", cnf=CNF_LABEL)
        self.entry_password = Entry(self.frame, cnf=CNF_ENTRY, show='*')
        self.bv_show_password = BooleanVar(self.frame)
        self.checkbox_show_password = Checkbutton(self.frame, text='نمایش رمز عبور', variable=self.bv_show_password, cnf=CNF_CHB, command=self.show_password)
        self.btn_login = Button(self.frame, text='ورود به حساب کاربری', cnf=CNF_BTN, command=self.login)
        self.btn_reset = Button(self.frame, text='ریست کردن', cnf=CNF_BTN, command=self.reset)
        self.label_username.grid(row=5, column=3, cnf=CNF_GRID)
        self.entry_username.grid(row=5, column=1, cnf=CNF_GRID)
        self.label_password.grid(row=7, column=3, cnf=CNF_GRID)
        self.entry_password.grid(row=7, column=1, cnf=CNF_GRID)
        self.checkbox_show_password.grid(row=11, column=3, cnf=CNF_GRID)
        self.btn_login.grid(row=13, column=3, cnf=CNF_GRID)
        self.btn_reset.grid(row=13, column=1, cnf=CNF_GRID)
        self.entry_username.bind('<Return>', lambda e: self.entry_password.focus_set())
        self.entry_password.bind('<Return>', self.login)

    def show_password(self):
        if self.bv_show_password.get():
            self.entry_password.config(show='')
        else:
            self.entry_password.config(show='*')

    def login(self, event=None):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if username=="":
            msb.showerror("ارور نام کاربری", "نام کاربری نمی تواند خالی باشد")
            self.entry_username.focus_set()
            return
        if password=="":
            msb.showerror("ارور رمز عبور", "رمز عبور نمی تواند خالی باشد")
            self.entry_password.focus_set()
            return
        result_message, person = self.connection.login(username, password)
        if result_message == "ok":
            self.root.withdraw()
            self.entry_password.delete(0, END)
            if person.access_level==1:
                self.admin_window.deiconify()
            elif person.access_level==2:
                self.staff_window.deiconify()
            else:
                self.root.deiconify()
            msb.showinfo("پیام موفقیت", f"خوش آمدی {person.name} {person.surname}")
        else:
            msb.showerror("ارور", result_message)

    def reset(self):
        self.bv_show_password.set(False)
        self.show_password()
        self.entry_username.delete(0, END)
        self.entry_password.delete(0, END)
        self.entry_username.focus_set()

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)
