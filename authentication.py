from ui_settings import *
from PIL import Image, ImageTk
from connection import Connection
from functions import calculate_fn, get_formula_parameters, how_many_times_parameters_variable_name_used_in_other_formulas, what_is_variable_name_problem, what_is_formula_problem, get_jnow, round4, jdatetime, datetime
from models import Part, Place, Staff, Parameter, ParameterLog
import win32api
from threading import Thread
from time import sleep
from decimal import Decimal
import os


class MyWindows():
    def __init__(self, connection: Connection, root: Tk):
        self.connection = connection
        self.root = root
        self.frame = Frame(self.root, bg=COLORS['BG'])
        self.S_WIDTH = self.root.winfo_screenwidth()
        self.S_HEIGHT= self.root.winfo_screenheight()

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    # چون پارامتر ویجت ارث بری دوگانه از پارامتر و مای ویندوز داره و پارامتر ها خودشون متغیری به
    # اسم پلیس برای مکان دارن، با این تابع پلیس به مشکل میخورد. به خاطر همین اسمش رو عوض کردم و 
    # گذاشتم پلیس ویجت که اگه یه روزی بخوام استفاده کنم داشته باشم تابعش رو.
    def place_widget(self, *args, **kwargs):
        self.frame.place(*args, **kwargs)


class LoginForm(MyWindows):
    def __init__(self, connection: Connection, root: Tk):
        super().__init__(connection, root)
        self.label_username = Label(self.frame, text="نام کاربری", cnf=CNF_LABEL)
        self.entry_username = Entry(self.frame, cnf=CNF_ENTRY)
        self.entry_username.focus_set()
        self.label_password = Label(self.frame, text="رمز عبور", cnf=CNF_LABEL)
        self.entry_password = Entry(self.frame, cnf=CNF_ENTRY, show='*')
        self.entry_username.insert(0, 'admin') # در پایان حذف شود
        self.entry_password.insert(0, 'admin') # در پایان حذف شود
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
        result_message, self.user = self.connection.login(username, password)
        if result_message == "ok":
            self.root.withdraw()
            StaffWindow(self.connection, self.root, self.user).grid()
        else:
            msb.showerror("ارور", result_message)

    def reset(self):
        self.bv_show_password.set(False)
        self.show_password()
        self.entry_username.delete(0, END)
        self.entry_password.delete(0, END)
        self.entry_username.focus_set()


class StaffWindow(MyWindows):
    def __init__(self, connection: Connection, root: Tk, user: Staff):
        super().__init__(connection, root)
        global date_picker, signal, sheet_state
        sheet_state = 'insert'
        signal = 0 # برای این که وقتی یه آپدیتی کردیم رو یه پارامتر، ظاهر برنامه رو رفرش کنیم و به تابع رفرش یو آی این کلاس دسترسی داشته باشیم.
        self.logged_parts_names = set() # یه لیست از پارت هایی که در تاریخ فعلی لاگ رو ثبت کردند. البته اول لیست گرفته بودم. بعد گفتم مجموعه کنم بهتره. اگه ثبت کردند، اسمشون میره تو این مجموعه که دیگه نتونن ثبت کنن و فقط بتونن ویرایش کنن. اول کار هیچ کس ثبت نکرده، پس فقط یه مجموعه خالی داریم. هر بخشی که ثبت کرد وارد این مجموعه میشه و بعد از اون فقط میتونه ویرایش کنه.
        self.user = user
        self.main_window = Toplevel(self.frame)
        self.main_window.title(f'حساب کاربری {self.user}')
        self.main_window.config(bg=COLORS['BG'])
        self.main_window.state('zoomed')
        self.main_window.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.main_window.iconbitmap(r"icons/counter_icon.ico")
        self.tab_control = ttk.Notebook(self.main_window) 
        self.tab_control.pack(anchor='n')
        self.frame_change_password_tab = Frame(self.tab_control, bg=COLORS['BG'])
        self.frame_add_statistics_tab = Frame(self.tab_control, bg=COLORS['BG'])
        self.tab_control.add(self.frame_change_password_tab, text ='تغییر رمز عبور')
        if self.user.access_level==1:
            self.frame_add_part_tab = Frame(self.tab_control, bg=COLORS['BG'])
            self.frame_add_place_tab = Frame(self.tab_control, bg=COLORS['BG'])
            self.frame_add_counter_tab = Frame(self.tab_control, bg=COLORS['BG'])
            self.frame_all_counters_tab = Frame(self.tab_control, bg=COLORS['BG'])
            self.frame_add_user_tab = Frame(self.tab_control, bg=COLORS['BG'])
            self.frame_set_default_date_tab = Frame(self.tab_control, bg=COLORS['BG'])
            self.frame_set_color_theme_tab = Frame(self.tab_control, bg=COLORS['BG'])
            self.tab_control.add(self.frame_set_color_theme_tab, text ='تغییر رنگ تم برنامه')
            self.tab_control.add(self.frame_set_default_date_tab, text ='تاریخ پیش فرض')
            self.tab_control.add(self.frame_add_user_tab, text ='افزودن کاربر جدید')
            self.tab_control.add(self.frame_all_counters_tab, text ='پارامترهای موجود')
            self.tab_control.add(self.frame_add_counter_tab, text ='افزودن پارامتر جدید')
            self.tab_control.add(self.frame_add_place_tab, text ='افزودن مکان جدید')
            self.tab_control.add(self.frame_add_part_tab, text ='افزودن بخش جدید')
        self.tab_control.add(self.frame_add_statistics_tab, text ='ثبت آمار')
        self.tab_control.select(self.frame_add_statistics_tab)

        ###################################### frame_add_statistics ######################################
        self.img_save           = Image.open(r'icons/save.png')
        self.img_update         = Image.open(r'icons/update.png')
        self.img_refresh        = Image.open(r'icons/refresh.png')
        self.img_save           = self.img_save         .resize((SAVE_ICON_SIZE, SAVE_ICON_SIZE))
        self.img_update         = self.img_update       .resize((UPDATE_ICON_SIZE, UPDATE_ICON_SIZE))
        self.img_refresh        = self.img_refresh      .resize((REFRESH_ICON_SIZE, REFRESH_ICON_SIZE))
        self.img_save           = ImageTk.PhotoImage(self.img_save)
        self.img_update         = ImageTk.PhotoImage(self.img_update)
        self.img_refresh        = ImageTk.PhotoImage(self.img_refresh)
        self.frame_add_statistics = Frame(self.frame_add_statistics_tab, cnf=CNF_FRM)
        self.frame_add_statistics.pack(side=RIGHT, anchor='ne')
        self.tab_control_frame = ttk.Notebook(self.frame_add_statistics)
        self.tab_control_frame.pack(side=TOP, expand=True, fill='both')
        self.tab_control_frame.bind('<Button-1>', self.disable_confirm_buttons)
        self.tab_control_frame.bind('<Key>', self.disable_confirm_buttons)
        self.tab_control_frame.bind('<ButtonRelease-1>', self.enable_btns_without_filling_counter_widgets)
        self.bottom_frame = Frame(self.frame_add_statistics, bg=COLORS['BG'])
        self.bottom_frame.pack(side=BOTTOM, expand=True, fill='x')
        self.bottom_frame_right = Frame(self.bottom_frame, bg=COLORS['BG'])
        self.bottom_frame_right.pack(side=RIGHT, expand=True, fill='both')
        self.bottom_frame_left = Frame(self.bottom_frame, bg=COLORS['BG'])
        self.bottom_frame_left.pack(side=LEFT)
        date_picker = DatePicker(self.connection, self.bottom_frame_right)
        date_picker.pack(side=RIGHT, expand=True, fill='both')
        self.btn_confirm_counter_log_insert = Button(self.bottom_frame_left, image=self.img_save, state='disabled', font=FONT2, cnf=CNF_BTN, command=self.confirm_log_insert)
        # self.btn_confirm_counter_log_insert.pack(side=LEFT, padx=PADX) # تو ورژنی که خواسته بود گفت که حذف بشه موقعی که فعال نیست.
        self.btn_confirm_counter_log_update = Button(self.bottom_frame_left, image=self.img_update, state='disabled', font=FONT2, cnf=CNF_BTN, command=self.confirm_log_update)
        self.btn_confirm_counter_log_update.pack(side=LEFT, padx=PADX)
        self.btn_refresh_counter_logs = Button(self.bottom_frame_left, image=self.img_refresh, font=FONT2, cnf=CNF_BTN, command=lambda: date_picker.time_delta(0))
        self.btn_refresh_counter_logs.pack(side=RIGHT, padx=PADX)
        self.seed_tabs_of_parts()

        ###################################### frame_change_users_password ######################################
        self.frame_change_users_password = LabelFrame(self.frame_change_password_tab, cnf=CNF_LBL_FRM)
        self.frame_change_users_password.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
        # self.frame_change_users_password.place(relx=0.36, rely=0.04, relwidth=1, relheight=1)
        self.label_username_change_users_password = Label(self.frame_change_users_password, text="نام کاربری", cnf=CNF_LABEL)
        self.entry_username_change_users_password = Entry(self.frame_change_users_password, cnf=CNF_ENTRY_USER)
        self.entry_username_change_users_password.insert(0, self.user.username)
        self.entry_username_change_users_password.config(state='readonly')
        self.label_old_password_change_users_password = Label(self.frame_change_users_password, text="رمز عبور قبلی", cnf=CNF_LABEL)
        self.entry_old_password_change_users_password = Entry(self.frame_change_users_password, cnf=CNF_ENTRY_USER, show='*')
        self.label_password1_change_users_password = Label(self.frame_change_users_password, text="رمز عبور جدید", cnf=CNF_LABEL)
        self.entry_password1_change_users_password = Entry(self.frame_change_users_password, cnf=CNF_ENTRY_USER, show='*')
        self.label_password2_change_users_password = Label(self.frame_change_users_password, text="تکرار رمز عبور جدید", cnf=CNF_LABEL)
        self.entry_password2_change_users_password = Entry(self.frame_change_users_password, cnf=CNF_ENTRY_USER, show='*')
        self.bv_show_password_change_users_password = BooleanVar(self.frame_change_users_password)
        self.checkbox_show_password_change_users_password = Checkbutton(self.frame_change_users_password, text='نمایش رمز عبور', variable=self.bv_show_password_change_users_password, cnf=CNF_CHB, command=self.show_password_change_users_password)
        self.btn_change_users_password = Button(self.frame_change_users_password, text='تغییر رمز عبور', cnf=CNF_BTN, command=self.change_users_password)
        self.label_username_change_users_password.grid(row=5, column=3, cnf=CNF_GRID)
        self.entry_username_change_users_password.grid(row=5, column=1, cnf=CNF_GRID)
        self.label_old_password_change_users_password.grid(row=6, column=3, cnf=CNF_GRID)
        self.entry_old_password_change_users_password.grid(row=6, column=1, cnf=CNF_GRID)
        self.label_password1_change_users_password.grid(row=7, column=3, cnf=CNF_GRID)
        self.entry_password1_change_users_password.grid(row=7, column=1, cnf=CNF_GRID)
        self.label_password2_change_users_password.grid(row=9, column=3, cnf=CNF_GRID)
        self.entry_password2_change_users_password.grid(row=9, column=1, cnf=CNF_GRID)
        self.checkbox_show_password_change_users_password.grid(row=11, column=3, cnf=CNF_GRID)
        self.btn_change_users_password.grid(row=13, column=3, cnf=CNF_GRID)
        self.entry_old_password_change_users_password.bind('<Return>', lambda e: self.entry_password1_change_users_password.focus_set())
        self.entry_password1_change_users_password.bind('<Return>', lambda e: self.entry_password2_change_users_password.focus_set())
        self.entry_password2_change_users_password.bind('<Return>', self.change_users_password)

        if self.connection.user.access_level==1:
            ###################################### frame_set_color_theme ######################################
            self.frame_set_color_theme = LabelFrame(self.frame_set_color_theme_tab, cnf=CNF_LBL_FRM)
            self.frame_set_color_theme.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            # self.frame_set_color_theme.place(relx=0.36, rely=0.04, relwidth=1, relheight=1)
            self.btn_set_theme_bg_color = Button(self.frame_set_color_theme, text='رنگ پس زمینه', cnf=CNF_BTN, command=lambda: self.select_color('BG'))
            self.btn_set_theme_fg_color = Button(self.frame_set_color_theme, text='رنگ اصلی نوشته ها', cnf=CNF_BTN, command=lambda: self.select_color('FG'))
            self.btn_set_theme_alarm_color = Button(self.frame_set_color_theme, text='رنگ آلارم', cnf=CNF_BTN, command=lambda: self.select_color('ALARM_COLOR'))
            self.btn_set_theme_warning_color = Button(self.frame_set_color_theme, text='رنگ هشدار', cnf=CNF_BTN, command=lambda: self.select_color('WARNING_COLOR'))
            self.btn_set_theme_ok_color = Button(self.frame_set_color_theme, text='رنگ بدون مشکل', cnf=CNF_BTN, command=lambda: self.select_color('OK_COLOR'))
            self.btn_set_theme_disabled_bg_color = Button(self.frame_set_color_theme, text='رنگ پس زمینه غیر فعال', cnf=CNF_BTN, command=lambda: self.select_color('DISABLED_BG'))
            self.btn_set_theme_disabled_fg_color = Button(self.frame_set_color_theme, text='رنگ نوشته غیر فعال', cnf=CNF_BTN, command=lambda: self.select_color('DISABLED_FG'))
            self.btn_set_theme_bg_lighter_color = Button(self.frame_set_color_theme, text='رنگ پس زمینه روشن تر', cnf=CNF_BTN, command=lambda: self.select_color('BG_LIGHTER'))
            self.btn_set_theme_fg2_color = Button(self.frame_set_color_theme, text='رنگ دوم نوشته ها', cnf=CNF_BTN, command=lambda: self.select_color('FG2'))
            self.treev_theme = ttk.Treeview(self.frame_set_color_theme, height=6, selectmode ='browse', show='headings')
            self.treev_theme.grid(row=3, rowspan=3, column=2, columnspan=10, sticky='news')
            self.treev_theme["columns"] = ("1", "2")
            self.treev_theme.column("1", width = 400, anchor ='c')
            self.treev_theme.column("2", width = 100, anchor ='c')
            self.treev_theme.heading("1", text ="بخش تست تم برنامه", anchor='c')
            self.treev_theme.heading("2", text ="ردیف", anchor='c')
            self.treev_theme.insert("", 1, values=('متن تستی اول', 1))
            self.treev_theme.insert("", 2, values=('متن تستی دوم', 2))
            self.btn_set_theme_bg_color.grid(row=1, column=6, cnf=CNF_GRID)
            self.btn_set_theme_fg_color.grid(row=1, column=5, cnf=CNF_GRID)
            self.btn_set_theme_alarm_color.grid(row=1, column=4, cnf=CNF_GRID)
            self.btn_set_theme_warning_color.grid(row=1, column=3, cnf=CNF_GRID)
            self.btn_set_theme_ok_color.grid(row=1, column=2, cnf=CNF_GRID)
            self.btn_set_theme_disabled_bg_color.grid(row=2, column=6, cnf=CNF_GRID)
            self.btn_set_theme_disabled_fg_color.grid(row=2, column=5, cnf=CNF_GRID)
            self.btn_set_theme_bg_lighter_color.grid(row=2, column=4, cnf=CNF_GRID)
            self.btn_set_theme_fg2_color.grid(row=2, column=3, cnf=CNF_GRID)
            self.btn_confirm_theme_color = Button(self.frame_set_color_theme, text='تایید رنگ بندی انتخاب شده', cnf=CNF_BTN, font=FONT2, command=self.confirm_theme_color)
            self.btn_confirm_theme_color.grid(row=5, column=1, cnf=CNF_GRID)

            ###################################### frame_set_default_date ######################################
            self.frame_set_default_date = LabelFrame(self.frame_set_default_date_tab, cnf=CNF_LBL_FRM)
            self.frame_set_default_date.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            # self.frame_set_default_date.place(relx=0.36, rely=0.04, relwidth=1, relheight=1)
            self.label_set_default_date = Label(self.frame_set_default_date, text='تاریخ پیش فرض', cnf=CNF_LABEL)
            self.entry_set_default_date = ttk.Combobox(self.frame_set_default_date, values=DEFAULT_DATE_VALUES, font=FONT, width=WORDS_WIDTH, justify='center')
            self.entry_set_default_date.insert(0, DEFAULT_DATE_VALUES[0])
            self.entry_set_default_date.config(state='readonly')
            self.btn_set_default_date = Button(self.frame_set_default_date, text='تایید', cnf=CNF_BTN, font=FONT2, command=self.confirm_default_date)
            self.label_set_default_date.grid(row=1, column=3, cnf=CNF_GRID)
            self.entry_set_default_date.grid(row=1, column=2, cnf=CNF_GRID)
            self.btn_set_default_date.grid(row=1, column=1, cnf=CNF_GRID)

            ############################################## frame_user ##############################################
            self.frame_user = LabelFrame(self.frame_add_user_tab, cnf=CNF_LBL_FRM)
            self.frame_user.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            # self.frame_user.place(relx=0.36, rely=0.04, relwidth=1, relheight=1)
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
            self.entry_name.bind('<Return>', lambda e: self.entry_surname.focus_set())
            self.entry_surname.bind('<Return>', lambda e: self.entry_username.focus_set())
            self.entry_username.bind('<Return>', lambda e: self.entry_password1.focus_set())
            self.entry_password1.bind('<Return>', lambda e: self.entry_password2.focus_set())
            self.entry_password2.bind('<Return>', self.create_account)

            ############################################# frame_counter #############################################
            self.frame_counter = LabelFrame(self.frame_add_counter_tab, cnf=CNF_LBL_FRM)
            self.frame_counter.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            self.label_counter_part = Label(self.frame_counter, text="بخش پارامتر", cnf=CNF_LABEL)
            self.entry_counter_part = ttk.Combobox(self.frame_counter, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')
            self.entry_counter_part.bind("<<ComboboxSelected>>", self.show_places_of_this_part)
            self.label_counter_place = Label(self.frame_counter, text="مکان پارامتر", cnf=CNF_LABEL)
            self.entry_counter_place = ttk.Combobox(self.frame_counter, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')
            self.label_counter_name = Label(self.frame_counter, text="نام پارامتر", cnf=CNF_LABEL)
            self.entry_counter_name = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER, justify='right')
            # self.entry_counter_name.bind('<FocusIn>', lambda e: self.entry_counter_name.select_range(0,END))
            self.label_counter_type = Label(self.frame_counter, text="نوع پارامتر", cnf=CNF_LABEL)
            self.entry_counter_type = ttk.Combobox(self.frame_counter, values=PARAMETER_TYPES, font=FONT, width=WORDS_WIDTH, justify='center')
            self.entry_counter_type.insert(0, PARAMETER_TYPES[0])
            self.entry_counter_type.config(state='readonly')
            self.entry_counter_type.bind("<<ComboboxSelected>>", self.check_counter_type)
            self.label_counter_unit = Label(self.frame_counter, text="واحد اندازه گیری", cnf=CNF_LABEL)
            self.entry_counter_unit = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            # self.entry_counter_unit.bind('<FocusIn>', lambda e: self.entry_counter_unit.select_range(0,END))
            self.label_counter_default_value = Label(self.frame_counter, text="مقدار پیش فرض", cnf=CNF_LABEL)
            self.entry_counter_default_value = ttk.Combobox(self.frame_counter, values=DEFAULT_VALUES, font=FONT, width=WORDS_WIDTH, justify='center')
            self.entry_counter_default_value.insert(0, DEFAULT_VALUES[0])
            self.entry_counter_default_value.config(state='readonly')
            self.label_counter_variable_name = Label(self.frame_counter, text="نام متغیر", cnf=CNF_LABEL)
            self.entry_counter_variable_name = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            # self.entry_counter_variable_name.bind('<FocusIn>', lambda e: self.entry_counter_variable_name.select_range(0,END))
            self.label_counter_warning_lower_bound = Label(self.frame_counter, text="حد پایین هشدار", cnf=CNF_LABEL)
            self.entry_counter_warning_lower_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            self.entry_counter_warning_lower_bound.insert(0, 0)
            # self.entry_counter_warning_lower_bound.bind('<FocusIn>', lambda e: self.entry_counter_variable_name.select_range(0,END))
            self.label_counter_warning_upper_bound = Label(self.frame_counter, text="حد بالای هشدار", cnf=CNF_LABEL)
            self.entry_counter_warning_upper_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            # self.entry_counter_warning_upper_bound.bind('<FocusIn>', lambda e: self.entry_counter_warning_upper_bound.select_range(0,END))
            self.label_counter_alarm_lower_bound = Label(self.frame_counter, text="حد پایین آلارم", cnf=CNF_LABEL)
            self.entry_counter_alarm_lower_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            self.entry_counter_alarm_lower_bound.insert(0, 0)
            # self.entry_counter_alarm_lower_bound.bind('<FocusIn>', lambda e: self.entry_counter_alarm_lower_bound.select_range(0,END))
            self.label_counter_alarm_upper_bound = Label(self.frame_counter, text="حد بالای آلارم", cnf=CNF_LABEL)
            self.entry_counter_alarm_upper_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            # self.entry_counter_alarm_upper_bound.bind('<FocusIn>', lambda e: self.entry_counter_alarm_upper_bound.select_range(0,END))
            self.label_counter_formula = Label(self.frame_counter, text="فرمول", cnf=CNF_LABEL)
            self.entry_counter_formula = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER, width=WORDS_WIDTH*2)
            self.entry_counter_formula.insert(0, 'b-a')
            # self.entry_counter_formula.bind('<FocusIn>', lambda e: self.entry_counter_formula.select_range(0,END))
            self.btn_counter_register = Button(self.frame_counter, text='ایجاد پارامتر', cnf=CNF_BTN, command=self.create_parameter)
            self.btn_counter_update = Button(self.frame_counter, text='ویرایش پارامتر', cnf=CNF_BTN, command=self.update_parameter)
            self.btn_counter_delete = Button(self.frame_counter, text='حذف پارامتر', cnf=CNF_BTN, command=self.delete_parameter)
            self.label_counter_part.grid(row=1, column=7, cnf=CNF_GRID)
            self.entry_counter_part.grid(row=1, column=5, cnf=CNF_GRID)
            self.label_counter_place.grid(row=1, column=3, cnf=CNF_GRID)
            self.entry_counter_place.grid(row=1, column=1, cnf=CNF_GRID)
            self.label_counter_name.grid(row=3, column=7, cnf=CNF_GRID)
            self.entry_counter_name.grid(row=3, column=5, cnf=CNF_GRID)
            self.label_counter_type.grid(row=3, column=3, cnf=CNF_GRID)
            self.entry_counter_type.grid(row=3, column=1, cnf=CNF_GRID)
            self.label_counter_unit.grid(row=5, column=7, cnf=CNF_GRID)
            self.entry_counter_unit.grid(row=5, column=5, cnf=CNF_GRID)
            self.label_counter_default_value.grid(row=5, column=3, cnf=CNF_GRID)
            self.entry_counter_default_value.grid(row=5, column=1, cnf=CNF_GRID)
            self.label_counter_variable_name.grid(row=9, column=7, cnf=CNF_GRID)
            self.entry_counter_variable_name.grid(row=9, column=5, cnf=CNF_GRID)
            self.label_counter_warning_lower_bound.grid(row=11, column=7, cnf=CNF_GRID)
            self.entry_counter_warning_lower_bound.grid(row=11, column=5, cnf=CNF_GRID)
            self.label_counter_warning_upper_bound.grid(row=11, column=3, cnf=CNF_GRID)
            self.entry_counter_warning_upper_bound.grid(row=11, column=1, cnf=CNF_GRID)
            self.label_counter_alarm_lower_bound.grid(row=13, column=7, cnf=CNF_GRID)
            self.entry_counter_alarm_lower_bound.grid(row=13, column=5, cnf=CNF_GRID)
            self.label_counter_alarm_upper_bound.grid(row=13, column=3, cnf=CNF_GRID)
            self.entry_counter_alarm_upper_bound.grid(row=13, column=1, cnf=CNF_GRID)
            self.label_counter_formula.grid(row=15, column=7, cnf=CNF_GRID)
            self.entry_counter_formula.grid(row=15, column=3, columnspan=3, cnf=CNF_GRID)
            self.btn_counter_register.grid(row=17, column=7, cnf=CNF_GRID)
            self.btn_counter_update.grid(row=17, column=5, cnf=CNF_GRID)
            self.btn_counter_delete.grid(row=17, column=3, cnf=CNF_GRID)
            self.entry_counter_part.bind('<Return>', lambda e: self.entry_counter_place.focus_set())
            self.entry_counter_place.bind('<Return>', lambda e: self.entry_counter_name.focus_set())
            self.entry_counter_name.bind('<Return>', lambda e: self.entry_counter_type.focus_set())
            self.entry_counter_type.bind('<Return>', lambda e: self.entry_counter_unit.focus_set())
            self.entry_counter_unit.bind('<Return>', lambda e: self.entry_counter_default_value.focus_set())
            self.entry_counter_default_value.bind('<Return>', lambda e: self.entry_counter_variable_name.focus_set())
            self.entry_counter_variable_name.bind('<Return>', lambda e: self.entry_counter_warning_lower_bound.focus_set())
            self.entry_counter_warning_lower_bound.bind('<Return>', lambda e: self.entry_counter_warning_upper_bound.focus_set())
            self.entry_counter_warning_upper_bound.bind('<Return>', lambda e: self.entry_counter_alarm_lower_bound.focus_set())
            self.entry_counter_alarm_lower_bound.bind('<Return>', lambda e: self.entry_counter_alarm_upper_bound.focus_set())
            self.entry_counter_alarm_upper_bound.bind('<Return>', lambda e: self.entry_counter_formula.focus_set())
            self.entry_counter_formula.bind('<Return>', self.create_parameter)

            ############################################# frame_part #############################################
            self.frame_part = LabelFrame(self.frame_add_part_tab, cnf=CNF_LBL_FRM)
            self.frame_part.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            # self.frame_part.place(relx=0.22, rely=0.08, relwidth=1, relheight=1)
            self.label_part_name = Label(self.frame_part, text="نام بخش", cnf=CNF_LABEL)
            self.entry_part_name = Entry(self.frame_part, cnf=CNF_ENTRY_COUNTER, justify='right')
            self.entry_part_name.bind("<Return>", self.create_part)
            self.btn_part_register = Button(self.frame_part, text='ایجاد بخش', cnf=CNF_BTN, command=self.create_part)
            self.btn_part_update = Button(self.frame_part, text='ویرایش بخش', cnf=CNF_BTN, command=self.update_part)
            self.btn_part_delete = Button(self.frame_part, text='حذف بخش', cnf=CNF_BTN, command=self.delete_part)
            self.label_part_name.grid(row=1, column=7, cnf=CNF_GRID)
            self.entry_part_name.grid(row=1, column=5, cnf=CNF_GRID)
            self.btn_part_register.grid(row=17, column=7, cnf=CNF_GRID)
            self.btn_part_update.grid(row=17, column=5, cnf=CNF_GRID)
            self.btn_part_delete.grid(row=17, column=3, cnf=CNF_GRID)
            self.treev_part = ttk.Treeview(self.frame_part, height=6, selectmode ='browse', show='headings')
            self.treev_part.grid(row=19, rowspan=3, column=1, columnspan=10, sticky='news')
            self.verscrlbar_part = ttk.Scrollbar(self.frame_part, orient ="vertical", command = self.treev_part.yview)
            self.verscrlbar_part.grid(row=19, rowspan=3, column=11, sticky='ns')
            self.treev_part.configure(yscrollcommand = self.verscrlbar_part.set)
            self.treev_part["columns"] = ("1", "2")
            self.treev_part.column("1", width = 300, anchor ='c')
            self.treev_part.column("2", width = 50, anchor ='c')
            self.treev_part.heading("1", text ="نام بخش", anchor='c')
            self.treev_part.heading("2", text ="ردیف", anchor='c')
            self.refresh_parts_tree_view()
            self.btn_up_tree_part = Button(self.frame_part, text='↑', cnf=CNF_BTN, font=FONT2, width=4, height=1, command=self.up_tree_part)
            self.btn_confirm_tree_part = Button(self.frame_part, text='تایید', cnf=CNF_BTN, font=FONT2, width=4, height=1, command=self.confirm_tree_part)
            self.btn_down_tree_part = Button(self.frame_part, text='↓', cnf=CNF_BTN, font=FONT2, width=4, height=1, command=self.down_tree_part)
            self.btn_up_tree_part.grid(row=19, column=0, cnf=CNF_GRID, sticky='s')
            self.btn_confirm_tree_part.grid(row=20, column=0, cnf=CNF_GRID)
            self.btn_down_tree_part.grid(row=21, column=0, cnf=CNF_GRID, sticky='n')

            ############################################# frame_place #############################################
            self.frame_place = LabelFrame(self.frame_add_place_tab, cnf=CNF_LBL_FRM)
            self.frame_place.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            # self.frame_place.place(relx=0.2, rely=0.02, relwidth=1, relheight=1)
            self.label_place_part_name = Label(self.frame_place, text="نام بخش", cnf=CNF_LABEL)
            self.entry_place_part_name = ttk.Combobox(self.frame_place, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')
            self.entry_place_part_name.bind("<<ComboboxSelected>>", self.refresh_places_frame_after_selecting_part)
            self.label_place_name = Label(self.frame_place, text="نام مکان", cnf=CNF_LABEL)
            self.entry_place_name = Entry(self.frame_place, cnf=CNF_ENTRY_COUNTER, justify='right', state='readonly')
            self.entry_place_name.bind("<Return>", self.create_place)
            self.btn_place_register = Button(self.frame_place, text='ایجاد مکان جدید', cnf=CNF_BTN, command=self.create_place)
            self.btn_place_update = Button(self.frame_place, text='ویرایش مکان', cnf=CNF_BTN, command=self.update_place)
            self.btn_place_delete = Button(self.frame_place, text='حذف مکان', cnf=CNF_BTN, command=self.delete_place)
            self.label_place_part_name.grid(row=1, column=7, cnf=CNF_GRID)
            self.entry_place_part_name.grid(row=1, column=5, cnf=CNF_GRID)
            self.label_place_name.grid(row=3, column=7, cnf=CNF_GRID)
            self.entry_place_name.grid(row=3, column=5, cnf=CNF_GRID)
            self.btn_place_register.grid(row=17, column=7, cnf=CNF_GRID)
            self.btn_place_update.grid(row=17, column=5, cnf=CNF_GRID)
            self.btn_place_delete.grid(row=17, column=3, cnf=CNF_GRID)
            self.treev_place = ttk.Treeview(self.frame_place, height=6, selectmode ='browse', show='headings')
            self.treev_place.grid(row=19, rowspan=3, column=1, columnspan=10, sticky='news')
            self.verscrlbar_place = ttk.Scrollbar(self.frame_place, orient ="vertical", command = self.treev_place.yview)
            self.verscrlbar_place.grid(row=19, rowspan=3, column=11, sticky='ns')
            self.treev_place.configure(yscrollcommand = self.verscrlbar_place.set)
            self.treev_place["columns"] = ("1", "2")
            self.treev_place.column("1", width = 300, anchor ='c')
            self.treev_place.column("2", width = 50, anchor ='c')
            self.treev_place.heading("1", text ="نام مکان", anchor='c')
            self.treev_place.heading("2", text ="ردیف", anchor='c')
            self.btn_up_tree_place = Button(self.frame_place, text='↑', cnf=CNF_BTN, font=FONT2, width=4, height=1, command=self.up_tree_place)
            self.btn_confirm_tree_place = Button(self.frame_place, text='تایید', cnf=CNF_BTN, font=FONT2, width=4, height=1, command=self.confirm_tree_place)
            self.btn_down_tree_place = Button(self.frame_place, text='↓', cnf=CNF_BTN, font=FONT2, width=4, height=1, command=self.down_tree_place)
            self.btn_up_tree_place.grid(row=19, column=0, cnf=CNF_GRID, sticky='s')
            self.btn_confirm_tree_place.grid(row=20, column=0, cnf=CNF_GRID)
            self.btn_down_tree_place.grid(row=21, column=0, cnf=CNF_GRID, sticky='n')
            self.refresh_parts_values_in_comboboxes()

            ######################################### frame_all_counters ##########################################
            self.frame_all_counters = LabelFrame(self.frame_all_counters_tab, cnf=CNF_LBL_FRM)
            self.frame_all_counters.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            # self.frame_all_counters.place(relx=0.2, rely=0.02, relwidth=1, relheight=1)
            self.treev_all_counters = ttk.Treeview(self.frame_all_counters, height=8, selectmode ='browse', show='headings')
            self.treev_all_counters.grid(row=19, rowspan=3, column=1, columnspan=10, sticky='news')
            self.treev_all_counters.bind("<Double-1>", self.change_counter_info)
            self.verscrlbar_all_counters = ttk.Scrollbar(self.frame_all_counters, orient ="vertical", command = self.treev_all_counters.yview)
            self.verscrlbar_all_counters.grid(row=19, rowspan=3, column=11, sticky='ns')
            self.treev_all_counters.configure(yscrollcommand = self.verscrlbar_all_counters.set)
            self.treev_all_counters["columns"] = ("1", "2", "3", "4")
            self.treev_all_counters.column("1", width = 350, anchor ='c')
            self.treev_all_counters.column("2", width = 300, anchor ='c')
            self.treev_all_counters.column("3", width = 300, anchor ='c')
            self.treev_all_counters.column("4", width = 100, anchor ='c')
            self.treev_all_counters.heading("1", text ="نام پارامتر", anchor='c')
            self.treev_all_counters.heading("2", text ="نام مکان", anchor='c')
            self.treev_all_counters.heading("3", text ="نام بخش", anchor='c')
            self.treev_all_counters.heading("4", text ="ردیف", anchor='c')
            self.btn_up_tree_all_counters = Button(self.frame_all_counters, text='↑', cnf=CNF_BTN, font=FONT2, width=4, height=1, command=self.up_tree_all_counters)
            self.btn_confirm_tree_all_counters = Button(self.frame_all_counters, text='تایید', cnf=CNF_BTN, font=FONT2, width=4, height=1, command=self.confirm_tree_all_counters)
            self.btn_down_tree_all_counters = Button(self.frame_all_counters, text='↓', cnf=CNF_BTN, font=FONT2, width=4, height=1, command=self.down_tree_all_counters)
            self.btn_up_tree_all_counters.grid(row=19, column=0, cnf=CNF_GRID, sticky='s')
            self.btn_confirm_tree_all_counters.grid(row=20, column=0, cnf=CNF_GRID)
            self.btn_down_tree_all_counters.grid(row=21, column=0, cnf=CNF_GRID, sticky='n')
            self.refresh_all_counters_treeview()
        
        Thread(target=self.refresh_ui_from_anywhere, daemon=True).start()
        self.refresh_ui()

    ######################################### change password functions #########################################
    # تابعی جهت بررسی این که پسووردها در بخش تغییر پسوورد نمایش داده شوند یا خیر
    def show_password_change_users_password(self):
        if self.bv_show_password_change_users_password.get():
            self.entry_old_password_change_users_password.config(show='')
            self.entry_password1_change_users_password.config(show='')
            self.entry_password1_change_users_password.focus_set()
            self.entry_password1_change_users_password.bind('<Return>', self.change_users_password)
            self.label_password2_change_users_password.grid_forget()
            self.entry_password2_change_users_password.grid_forget()
        else:
            self.entry_old_password_change_users_password.config(show='*')
            self.entry_password1_change_users_password.config(show='*')
            self.entry_password1_change_users_password.bind('<Return>', lambda e: self.entry_password2_change_users_password.focus_set())
            self.label_password2_change_users_password.grid(row=9, column=3, cnf=CNF_GRID)
            self.entry_password2_change_users_password.grid(row=9, column=1, cnf=CNF_GRID)
            self.entry_password2_change_users_password.focus_set()

    # تابعی جهت تغییر پسوورد کاربر فعلی
    def change_users_password(self, event=None):
        username = self.entry_username_change_users_password.get().strip()
        old_password = self.entry_old_password_change_users_password.get()
        password1 = self.entry_password1_change_users_password.get()
        password2 = self.entry_password2_change_users_password.get()
        if old_password=="":
            msb.showerror("ارور رمز عبور", "رمز عبور قبلی نمی تواند خالی باشد")
            self.entry_old_password_change_users_password.focus_set()
            return
        if password1=="":
            msb.showerror("ارور رمز عبور", "رمز عبور جدید نمی تواند خالی باشد")
            self.entry_password1_change_users_password.focus_set()
            return
        if self.bv_show_password_change_users_password.get()==False and password1!=password2:
            msb.showerror("ارور رمز عبور", "رمز عبور های جدید با یکدیگر مطابقت ندارند")
            self.entry_password2_change_users_password.focus_set()
            return
        result_message, result = self.connection.change_users_password(username, old_password, password1)
        if result_message == "ok":
            msb.showinfo("پیام موفقیت", f"رمز عبور نام کاربری {username} با موفقیت تغییر کرد")
        else:
            msb.showerror("ارور", result_message)

    ######################################### create account functions ##########################################
    # تابعی جهت نمایش پسووردها در قسمت ساخت اکانت
    def show_password(self):
        if self.bv_show_password.get():
            self.entry_password1.config(show='')
            self.entry_password1.focus_set()
            self.entry_password1.bind('<Return>', self.create_account)
            self.label_password2.grid_forget()
            self.entry_password2.grid_forget()
        else:
            self.entry_password1.config(show='*')
            self.entry_password1.bind('<Return>', lambda e: self.entry_password2.focus_set())
            self.label_password2.grid(row=9, column=3, cnf=CNF_GRID)
            self.entry_password2.grid(row=9, column=1, cnf=CNF_GRID)
            self.entry_password2.focus_set()
    
    # تابعی جهت ساخت اکانت
    def create_account(self, event=None):
        name = self.entry_name.get().strip()
        surname = self.entry_surname.get().strip()
        username = self.entry_username.get().strip()
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
            msb.showinfo("پیام موفقیت", f"نام کاربری {username} با موفقیت ساخته شد")
        else:
            msb.showerror("ارور", result_message)

    ######################################### create counter functions ##########################################
    # تابعی برای این که با انتخاب یک بخش، مکان های آن در کمبوباکس دوم نمایش داده شوند.
    def show_places_of_this_part(self, event=None):
        part_name = self.entry_counter_part.get()
        part_id, part_name, part_order = self.connection.get_part_by_title(part_name)
        places = self.connection.get_all_places_by_part_id(part_id)
        values = []
        for place in places:
            values.append(place.title)
        self.entry_counter_place.config(state='normal', values=values)
        self.entry_counter_place.delete(0, END)
        self.entry_counter_place.config(state='readonly')

    # تابعی برای این که وقتی نوع پارامتر انتخاب شد، کمبو باکس نوع مقدار پیش فرض تغییر کنه
    # و همچنین بعضی از باکس ها فعال یا غیر فعال بشن
    def check_counter_type(self, event=None, previous_type=DEFAULT_VALUES[0]):
        counter_type = self.entry_counter_type.get()
        self.entry_counter_default_value.config(state='normal')
        self.entry_counter_default_value.delete(0, END)
        if counter_type in PARAMETER_TYPES[0:2]: # یعنی یا کنتور معمولی باشه یا ثابت
            self.entry_counter_default_value.insert(0, previous_type)
            self.entry_counter_default_value.config(values=DEFAULT_VALUES)
        elif counter_type==PARAMETER_TYPES[2]: # یعنی از نوع محاسباتی باشه
            self.entry_counter_default_value.config(values=[])
        self.entry_counter_default_value.config(state='readonly')
        if counter_type==PARAMETER_TYPES[1]: # fixed:
            self.entry_counter_formula.delete(0, END)
            self.entry_counter_formula.config(state='readonly')
        else:
            self.entry_counter_formula.config(state='normal')

    # تابعی جهت ایجاد پارامتر
    def create_parameter(self, event=None):
        is_everything_ok = True # برای ایجاد پارامتر اول فرض میکنیم همه چی اوکی هست. اگه مشکلی پیش اومد فالسش میکنیم.
        part = self.entry_counter_part.get()
        place = self.entry_counter_place.get()
        name = self.entry_counter_name.get().strip()
        type = self.entry_counter_type.get()
        unit = self.entry_counter_unit.get().strip()
        default_value = self.entry_counter_default_value.get()
        variable_name = self.entry_counter_variable_name.get().strip()
        warning_lower_bound = self.entry_counter_warning_lower_bound.get().strip()
        warning_upper_bound = self.entry_counter_warning_upper_bound.get().strip()
        alarm_lower_bound = self.entry_counter_alarm_lower_bound.get().strip()
        alarm_upper_bound = self.entry_counter_alarm_upper_bound.get().strip()
        formula = self.entry_counter_formula.get().strip()
        formula_parameters = []
        # formula_parameters = self.entry_counter_formula_parameters.get().strip()
        if part == "":
            msb.showerror("خطا", "پارامتر مربوط به کدام بخش است؟")
            self.entry_counter_part.focus_set()
            return
        if place == "":
            msb.showerror("خطا", "پارامتر مربوط به کدام مکان است؟")
            self.entry_counter_place.focus_set()
            return
        if name == "":
            msb.showerror("خطا", "نام پارامتر را وارد کنید")
            self.entry_counter_name.focus_set()
            return
        if unit == "":
            unit=None
        parameters_variable_names = self.connection.get_all_parameters_variable_names()
        problem = what_is_variable_name_problem(variable_name, parameters_variable_names)
        if problem:
            msb.showerror("خطا", problem)
            self.entry_counter_variable_name.focus_set()
            return
        if warning_lower_bound == "":
            warning_lower_bound=0
        else:
            try:
                warning_lower_bound = float(warning_lower_bound)
            except:
                msb.showerror("خطا", "لطفا حد پایین هشدار را به صورت عددی وارد کنید")
                self.entry_counter_warning_lower_bound.focus_set()
                return
        if warning_upper_bound == "":
            warning_upper_bound=9999999999
        else:
            try:
                warning_upper_bound = float(warning_upper_bound)
            except:
                msb.showerror("خطا", "لطفا حد بالای هشدار را به صورت عددی وارد کنید")
                self.entry_counter_warning_upper_bound.focus_set()
                return
        if alarm_lower_bound == "":
            alarm_lower_bound=0
        else:
            try:
                alarm_lower_bound = float(alarm_lower_bound)
            except:
                msb.showerror("خطا", "لطفا حد پایین آلارم را به صورت عددی وارد کنید")
                self.entry_counter_alarm_lower_bound.focus_set()
                return
        if alarm_upper_bound == "":
            alarm_upper_bound=9999999999
        else:
            try:
                alarm_upper_bound = float(alarm_upper_bound)
            except:
                msb.showerror("خطا", "لطفا حد بالای آلارم را به صورت عددی وارد کنید")
                self.entry_counter_alarm_upper_bound.focus_set()
                return
        if formula != "":
            result = what_is_formula_problem(formula, formula_parameters, variable_name, parameters_variable_names, type)
            if isinstance(result, str): # یعنی اگه یه استرینگ داده بود، مشکلی هست. پس ارور رو نشون بده.
                msb.showerror("خطا", result)
                self.entry_counter_formula.focus_set()
                return
            elif isinstance(result, list):
                message = "پارامترهای تشخیص داده شده به ترتیب به صورت زیر است\n"
                for i in result:
                    message += f"{i}\n"
                message+= "در صورتی که صحیح است، تایید کنید و در غیر این صورت، فرمول را اصلاح کنید"
                self.root.bell()
                is_everything_ok = msb.askyesno("تایید", message)
                if is_everything_ok:
                    result = what_is_formula_problem(formula, result, variable_name, parameters_variable_names, type)
                    if isinstance(result, list):
                        is_everything_ok=True
                    else:
                        is_everything_ok=False
                        msb.showerror('خطا', result)
        if formula == "" and type in [PARAMETER_TYPES[0], PARAMETER_TYPES[2]]:
            msb.showerror("خطا", "برای پارامترهای محاسباتی و کنتور، فرمول نمیتواند خالی باشد")
            self.entry_counter_formula.focus_set()
            return
        if is_everything_ok:
            result_message, _ = self.connection.create_parameter(name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place)
        else:
            return
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"پارامتر {name} با موفقیت در مکان {place} از بخش {part} ساخته شد")
            self.refresh_ui()
        else:
            msb.showerror("خطا", result_message)
            print(_)

    # تابعی جهت ویرایش پارامتر
    def update_parameter(self):
        is_everything_ok = True # برای تغییر پارامتر اول فرض میکنیم همه چی اوکی هست. اگه مشکلی پیش اومد فالسش میکنیم.
        part = self.entry_counter_part.get()
        place = self.entry_counter_place.get()
        name = self.entry_counter_name.get().strip()
        type = self.entry_counter_type.get()
        unit = self.entry_counter_unit.get().strip()
        default_value = self.entry_counter_default_value.get()
        variable_name = self.entry_counter_variable_name.get().strip()
        warning_lower_bound = self.entry_counter_warning_lower_bound.get().strip()
        warning_upper_bound = self.entry_counter_warning_upper_bound.get().strip()
        alarm_lower_bound = self.entry_counter_alarm_lower_bound.get().strip()
        alarm_upper_bound = self.entry_counter_alarm_upper_bound.get().strip()
        formula = self.entry_counter_formula.get().strip()
        formula_parameters = []
        # formula_parameters = self.entry_counter_formula_parameters.get().strip()
        if part == "":
            msb.showerror("خطا", "پارامتر مربوط به کدام بخش است؟")
            self.entry_counter_part.focus_set()
            return
        if place == "":
            msb.showerror("خطا", "پارامتر مربوط به کدام مکان است؟")
            self.entry_counter_place.focus_set()
            return
        if name == "":
            msb.showerror("خطا", "نام پارامتر را وارد کنید")
            self.entry_counter_name.focus_set()
            return
        if unit == "":
            unit=None
        this_parameter = self.connection.get_parameter_by_variable_name(variable_name)
        if this_parameter == None:
            msb.showerror("خطا", "پارامتر با نام متغیر نوشته شده وجود ندارد")
            self.entry_counter_variable_name.focus_set()
            return
        if warning_lower_bound == "":
            warning_lower_bound=None
        else:
            try:
                warning_lower_bound = float(warning_lower_bound)
            except:
                msb.showerror("خطا", "لطفا حد پایین هشدار را به صورت عددی وارد کنید")
                self.entry_counter_warning_lower_bound.focus_set()
                return
        if warning_upper_bound == "":
            warning_upper_bound=None
        else:
            try:
                warning_upper_bound = float(warning_upper_bound)
            except:
                msb.showerror("خطا", "لطفا حد بالای هشدار را به صورت عددی وارد کنید")
                self.entry_counter_warning_upper_bound.focus_set()
                return
        if alarm_lower_bound == "":
            alarm_lower_bound=None
        else:
            try:
                alarm_lower_bound = float(alarm_lower_bound)
            except:
                msb.showerror("خطا", "لطفا حد پایین آلارم را به صورت عددی وارد کنید")
                self.entry_counter_alarm_lower_bound.focus_set()
                return
        if alarm_upper_bound == "":
            alarm_upper_bound=None
        else:
            try:
                alarm_upper_bound = float(alarm_upper_bound)
            except:
                msb.showerror("خطا", "لطفا حد بالای آلارم را به صورت عددی وارد کنید")
                self.entry_counter_alarm_upper_bound.focus_set()
                return
        if formula != "":
            parameters_variable_names = self.connection.get_all_parameters_variable_names()
            result = what_is_formula_problem(formula, formula_parameters, variable_name, parameters_variable_names, type)
            if isinstance(result, str): # یعنی اگه یه استرینگ داده بود، مشکلی هست. پس ارور رو نشون بده.
                msb.showerror("خطا", result)
                self.entry_counter_formula.focus_set()
                return
            elif isinstance(result, list):
                message = "پارامترهای تشخیص داده شده به ترتیب به صورت زیر است\n"
                for i in result:
                    message += f"{i}\n"
                message+= "در صورتی که صحیح است، تایید کنید و در غیر این صورت، فرمول را اصلاح کنید"
                self.root.bell()
                is_everything_ok = msb.askyesno("تایید", message)
                if is_everything_ok:
                    result = what_is_formula_problem(formula, result, variable_name, parameters_variable_names, type)
                    if isinstance(result, list):
                        is_everything_ok=True
                    else:
                        is_everything_ok=False
                        msb.showerror('خطا', result)
        if formula == "" and type in [PARAMETER_TYPES[0], PARAMETER_TYPES[2]]:
            msb.showerror("خطا", "برای پارامترهای محاسباتی و کنتور، فرمول نمیتواند خالی باشد")
            self.entry_counter_formula.focus_set()
            return
        if is_everything_ok:
            result_message, _ = self.connection.update_parameter(name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place)
        else:
            return
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"اطلاعات پارامتر با نام متغیر {variable_name} با موفقیت ویرایش شد")
            self.refresh_ui()
        else:
            msb.showerror("خطا", result_message)
            print(_)

    # تابعی جهت حذف پارامتر
    def delete_parameter(self):
        variable_name = self.entry_counter_variable_name.get().strip()
        this_parameter = self.connection.get_parameter_by_variable_name(variable_name)
        if this_parameter == None:
            msb.showerror("خطا", "پارامتر با نام متغیر نوشته شده وجود ندارد")
            self.entry_counter_variable_name.focus_set()
            return
        name = this_parameter.name
        id = this_parameter.id
        self.root.bell()
        answer = msb.askyesno("اطمینان", f"آیا از حذف پارامتر با نام {name} مطمئنید؟")
        if answer==False:
            return
        formulas = self.connection.get_all_parameters_formula()
        count = how_many_times_parameters_variable_name_used_in_other_formulas(variable_name, formulas)
        if count > 0:
            msb.showerror("خطا", f"از نام این پارامتر {count} بار در فرمول دیگر پارامترها استفاده شده است. به دلیل ایجاد مشکل در محاسبات و عملکرد کل دیتابیس، در حال حاضر از طریق این برنامه اجازه حذف این پارامتر را ندارید. ابتدا باید تمامی پارامترهایی که در فرمول خود از این پارامتر استفاده کرده اند را حذف یا ویرایش کنید تا به این پارامتر وابسته نباشند، سپس اقدام به حذف این پارامتر نمایید")
            self.entry_counter_variable_name.focus_set()
            return
        result_message, _ = self.connection.delete_parameter(id)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"پارامتر {name} با موفقیت حذف شد")
            self.refresh_ui()
        else:
            msb.showerror("خطا", result_message)

    # تابعی برای این که با دابل کلیک روی نام یک پارامتر در بخش نمایش آنها، جزییات آن را نمایش دهد و قابل تغییر باشد.
    def change_counter_info(self, event=None):
        try:
            item = self.treev_all_counters.selection()[0]
        except IndexError:
            msb.showwarning("هشدار", "برای انتخاب یک پارامتر باید روی پارامتر مربوطه دابل کلیک کنید")
            return
        id = self.treev_all_counters.item(item, "text")
        temp_counter = self.connection.get_parameter_by_id(id)
        temp_name, temp_place, temp_part = self.treev_all_counters.item(item, "values")[0:3]
        self.tab_control.select(self.frame_add_counter_tab)
        self.entry_counter_part.config(state='normal')
        self.entry_counter_place.config(state='normal')
        self.entry_counter_type.config(state='normal')
        # self.entry_counter_default_value.config(state='normal') یه باگی داشت که تو تابع چک کنتور تایپ با ورودی دادن درستش کردم. دیگه لازم نیست که این خط اینجا باشه. گذاشتم که دفعه بعد یادم باشه. دفعه بعد میتونم پاک کنم.
        self.entry_counter_formula.config(state='normal')
        self.entry_counter_part.delete(0, END)
        self.entry_counter_place.delete(0, END)
        self.entry_counter_name.delete(0, END)
        self.entry_counter_type.delete(0, END)
        self.entry_counter_unit.delete(0, END)
        # self.entry_counter_default_value.delete(0, END) همونی که بالا تر توضیح دادم. دفع بعد میتونم اینم پاک کنم.
        self.entry_counter_variable_name.delete(0, END)
        self.entry_counter_warning_lower_bound.delete(0, END)
        self.entry_counter_warning_upper_bound.delete(0, END)
        self.entry_counter_alarm_lower_bound.delete(0, END)
        self.entry_counter_alarm_upper_bound.delete(0, END)
        self.entry_counter_formula.delete(0, END)
        self.entry_counter_part.insert(0, temp_part)
        self.entry_counter_place.insert(0, temp_place)
        self.entry_counter_name.insert(0, temp_name)
        self.entry_counter_type.insert(0, temp_counter.type)
        # self.entry_counter_default_value.insert(0, temp_counter.default_value) این هم دفع بعد میتونم پاک کنم.
        self.entry_counter_variable_name.insert(0, temp_counter.variable_name)
        self.entry_counter_formula.insert(0, temp_counter.formula)
        if temp_counter.unit:
            self.entry_counter_unit.insert(0, temp_counter.unit)
        if temp_counter.warning_lower_bound:
            self.entry_counter_warning_lower_bound.insert(0, round4(temp_counter.warning_lower_bound))
        else:
            self.entry_counter_warning_lower_bound.insert(0, 0)
        if temp_counter.warning_upper_bound:
            self.entry_counter_warning_upper_bound.insert(0, round4(temp_counter.warning_upper_bound))
        if temp_counter.alarm_lower_bound:
            self.entry_counter_alarm_lower_bound.insert(0, round4(temp_counter.alarm_lower_bound))
        else:
            self.entry_counter_alarm_lower_bound.insert(0, 0)
        if temp_counter.alarm_upper_bound:
            self.entry_counter_alarm_upper_bound.insert(0, round4(temp_counter.alarm_upper_bound))
        self.entry_counter_part.config(state='readonly')
        self.entry_counter_place.config(state='readonly')
        self.entry_counter_type.config(state='readonly')
        self.entry_counter_default_value.config(state='readonly')
        # یه باگ داشت که مقدار پیش فرض رو درست نمینوشت. چون آخر سر تابع چک کنتور تایپ رو کال کرده
        # بودم که باعث میشد پاک بشه و همون مقدار اول پیش فرض برنامه داخلش نوشته بشه. به خاطر همین
        # به این تابع یه ورودی دادم که موقع آپدیت اذیت نکنه
        self.check_counter_type(previous_type=temp_counter.default_value)
        # تا اینجا اوکی هست. یه باگی داشت که وقتی رو تری ویو دابل کلیک میکردیم اینور نمیشد مکان
        # کنتور رو انتخاب کرد. باید حتما رو بخش کلیک میکردیم تا مکان هاش بیان. برای رفع این
        # باگ این کار های پایین رو انجام دادم.
        places = self.connection.get_all_places_by_part_id(temp_counter.part)
        new_values = []
        for p in places:
            p:Place
            new_values.append(p.title)
        self.entry_counter_place.config(values=new_values)        

    ########################################## create part functions ###########################################
    # تابعی جهت ساخت بخش
    def create_part(self, event=None):
        title = self.entry_part_name.get().strip()
        if title=="":
            msb.showerror("خطا", "نام بخش نمیتواند خالی باشد.")
            return
        result_message, _ = self.connection.create_part(title)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"بخش {title} با موفقیت ساخته شد.")
            self.refresh_ui()
            self.entry_part_name.delete(0, END)
        else:
            msb.showerror("خطا", result_message)
            print(_)
        self.entry_part_name.focus_set()

    # تابعی جهت ویرایش بخش
    def update_part(self, event=None):
        cur_item = self.treev_part.focus()
        temp = self.treev_part.item(cur_item)["values"]
        if temp in [None, '', ()]:
            msb.showerror('خطا', 'برای تغییر نام، ابتدا باید یک بخش را انتخاب کنید')
            return
        old_name = temp[0]
        id = self.treev_part.item(cur_item)["text"]
        new_name = self.entry_part_name.get().strip()
        if new_name=="":
            msb.showerror("خطا", "نام بخش نمیتواند خالی باشد.")
            return
        self.root.bell()
        answer = msb.askyesno("اطمینان", f"آیا از تغییر نام بخش {old_name} به {new_name} مطمئنید؟")
        if answer==False:
            return
        result_message, _ = self.connection.update_part(id, new_name)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"بخش {old_name} با موفقیت به {new_name} تغییر یافت")
            self.refresh_ui()
            self.entry_part_name.delete(0, END)
        else:
            msb.showerror("خطا", result_message)
            print(_)
        self.entry_part_name.focus_set()
    
    # تابعی جهت حذف بخش
    def delete_part(self, event=None):
        cur_item = self.treev_part.focus()
        temp = self.treev_part.item(cur_item)["values"]
        if temp in [None, '', ()]:
            msb.showerror('خطا', 'برای حذف بخش، ابتدا باید یک بخش را انتخاب کنید')
            return
        name = temp[0]
        id = self.treev_part.item(cur_item)["text"]
        self.root.bell()
        answer = msb.askyesno("اطمینان", f"آیا از حذف بخش {name} مطمئنید؟")
        if answer==False:
            return
        result_message, _ = self.connection.delete_part(id)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"بخش {name} با موفقیت حذف شد")
            self.refresh_ui()
            self.entry_part_name.delete(0, END)
        else:
            msb.showerror("خطا", result_message)
        self.entry_part_name.focus_set()

    # تابعی برای این که بعد از ساخت یک بخش، در ظاهر برنامه و
    # در کمبوباکس ها بخش های جدید ساخته شده هم نمایش داده شوند.
    def refresh_parts_values_in_comboboxes(self, event=None):
        parts = self.connection.get_all_parts()
        values = []
        for part in parts:
            values.append(part.title)
        self.entry_place_part_name.config(state='normal', values=values)
        self.entry_place_part_name.config(state='readonly')
        self.entry_counter_part.config(state='normal', values=values)
        self.entry_counter_part.config(state='readonly')
    
    # تابعی برای این که بعد از ساخت یک بخش، در ظاهر برنامه و
    # در تری ویوی مربوطه، بخش های جدید نمایش داده شوند.
    def refresh_parts_tree_view(self):
        self.treev_part.delete(*self.treev_part.get_children())
        parts = self.connection.get_all_parts()
        for i, part in enumerate(parts):
            self.treev_part.insert("", i, text=part.id, values=(part.title, i+1))
    
    # تابعی برای این که بشه اولویت نمایش یک بخش رو بالا برد
    def up_tree_part(self):
        cur_item = self.treev_part.focus()
        try:
            prev_item = self.treev_part.prev(cur_item)
            temp_text222 = self.treev_part.item(prev_item)['text']
            position222 = self.treev_part.item(prev_item)['values'][1]+1
            temp_values222 = self.treev_part.item(prev_item)['values'][0], position222 
        except:
            return
        temp_text = self.treev_part.item(cur_item)["text"]
        temp_values = self.treev_part.item(cur_item)["values"]
        position = temp_values[-1]-2
        new_child=self.treev_part.insert("", position, text=temp_text, values=(temp_values[0], position+1))
        self.treev_part.delete(cur_item)
        self.treev_part.insert("", position222, text=temp_text222, values=temp_values222)
        self.treev_part.delete(prev_item)
        self.treev_part.focus(new_child)
        self.treev_part.selection_set(new_child)
        
    # تابعی برای این که بشه اولویت نمایش یک بخش رو پایین آورد
    def down_tree_part(self):
        cur_item = self.treev_part.focus()
        try:
            next_item = self.treev_part.next(cur_item)
            temp_text222 = self.treev_part.item(next_item)['text']
            position222 = self.treev_part.item(next_item)['values'][1]-2
            temp_values222 = self.treev_part.item(next_item)['values'][0], position222+1
        except:
            return
        temp_text = self.treev_part.item(cur_item)["text"]
        temp_values = self.treev_part.item(cur_item)["values"]
        position = temp_values[-1]
        self.treev_part.insert("", position222, text=temp_text222, values=temp_values222)
        self.treev_part.delete(next_item)
        new_child=self.treev_part.insert("", position, text=temp_text, values=(temp_values[0], position+1))
        self.treev_part.delete(cur_item)
        self.treev_part.focus(new_child)
        self.treev_part.selection_set(new_child)
    
    # تابعی برای این که اولویت بخش ها رو به صورتی که تعیین کردیم در دیتابیس ذخیره کنه
    def confirm_tree_part(self, event=None):
        try:
            for item in self.treev_part.get_children():
                item = self.treev_part.item(item)
                id=int(item['text'])
                order=int(item['values'][-1])
                result_message, _ = self.connection.change_parts_order(id, order)
            if result_message=='ok':
                self.refresh_parts_values_in_comboboxes()
                msb.showinfo("پیام موفقیت", f"ترتیب بخش ها با موفقیت تغییر یافت")
                self.refresh_ui()
            else:
                msb.showerror("خطا", result_message)
                print(_)
        except UnboundLocalError:
            msb.showerror("خطا", f"ابتدا باید ترتیب بخش ها را مشخص کنید و سپس روی دکمه تایید بزنید.")

    ########################################## create place functions ##########################################
    # تابعی برای این که بعد از انتخاب کمبو باکس بخش، مقادیر کمبوباکس مکان هاش آپدیت بشن و نمایش داده بشن.
    def refresh_places_frame_after_selecting_part(self, event=None):
        part = self.entry_place_part_name.get()
        if part=="":
            self.entry_place_name.config(state='normal')
            self.entry_place_name.delete(0, END)
            self.entry_place_name.config(state='readonly')
            return
        self.entry_place_name.config(state='normal')
        part_id, part_title, part_sort = self.connection.get_part_by_title(part)
        self.refresh_places_tree_view(part_id)

    # تابعی برای ثبت یک مکان جدید
    def create_place(self, event=None):
        title = self.entry_place_name.get().strip()
        part = self.entry_place_part_name.get()
        if title=="" or part=="":
            msb.showerror("خطا", "نام مکان یا بخش نمیتواند خالی باشد.")
            return
        part_id, part_title, part_sort = self.connection.get_part_by_title(part)
        result_message, _ = self.connection.create_place(title, part_id)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"مکان {title} در بخش {part} با موفقیت ساخته شد.")
            self.refresh_places_tree_view(part_id)
            self.refresh_ui()
            # self.entry_place_name.delete(0, END) # گفتم شاید بخواد تو بخش های مختلف مکان همنام درست کنه کامنت کردم. ولی اگه بخوایم ریست کنیم گفتم سریع بشه آنکامنتش کرد.
        else:
            msb.showerror("خطا", result_message)
            print(_)
        self.entry_place_name.focus_set()
    
    # تابعی برای ویرایش یک مکان موجود
    def update_place(self, event=None):
        cur_item = self.treev_place.focus()
        temp = self.treev_place.item(cur_item)["values"]
        if temp in [None, '', ()]:
            msb.showerror('خطا', 'برای تغییر نام، ابتدا باید یک مکان را انتخاب کنید')
            return
        old_name = temp[0]
        id = self.treev_place.item(cur_item)["text"]
        new_name = self.entry_place_name.get().strip()
        part = self.entry_place_part_name.get()
        # این ایف پایین لازم نیست. اما گذاشتم باشه. چون کدش رو نوشته بودم گفتم دست نزنم که باگ
        # جدید نخوره. اما منطقا اگه برش دارم هم نباید مشکلی پیش بیاد.
        if new_name=="" or part=="":
            msb.showerror("خطا", "نام مکان یا بخش نمیتواند خالی باشد.")
            return
        self.root.bell()
        answer = msb.askyesno("اطمینان", f"آیا از تغییر نام مکان {old_name} به {new_name} مطمئنید؟")
        if answer==False:
            return
        part_id, part_title, part_sort = self.connection.get_part_by_title(part)
        result_message, _ = self.connection.update_place(id, new_name, part_id)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"نام مکان {old_name} در بخش {part} با موفقیت به {new_name} تغییر یافت")
            self.refresh_places_tree_view(part_id)
            self.refresh_ui()
        else:
            msb.showerror("خطا", result_message)
            print(_)
        self.entry_place_name.focus_set()

    # تابعی برای حذف یک مکان
    def delete_place(self, event=None):
        cur_item = self.treev_place.focus()
        temp = self.treev_place.item(cur_item)["values"]
        if temp in [None, '', ()]:
            msb.showerror('خطا', 'برای حذف، ابتدا باید یک مکان را انتخاب کنید')
            return
        name = temp[0]
        id = self.treev_place.item(cur_item)["text"]
        part = self.entry_place_part_name.get()
        self.root.bell()
        answer = msb.askyesno("اطمینان", f"آیا از حذف مکان {name} واقع در بخش {part} مطمئنید؟")
        if answer==False:
            return
        part_id, part_title, part_sort = self.connection.get_part_by_title(part)
        result_message, _ = self.connection.delete_place(id)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"مکان {name} از بخش {part} با موفقیت حذف شد")
            self.refresh_places_tree_view(part_id)
            self.refresh_ui()
        else:
            msb.showerror("خطا", result_message)
        self.entry_place_name.focus_set()

    # تابعی برای این که بعد از ساخت یک مکان در ظاهر برنامه و
    # در تری ویوی مربوطه، مکان های جدید نمایش داده شوند.
    def refresh_places_tree_view(self, part_id):
        self.treev_place.delete(*self.treev_place.get_children())
        places = self.connection.get_all_places_by_part_id(part_id)
        for i, place in enumerate(places):
            self.treev_place.insert("", i, text=place.id, values=(place.title, i+1))
               
    # تابعی برای این که بشه اولویت نمایش یک مکان رو بالا برد
    def up_tree_place(self):
        cur_item = self.treev_place.focus()
        try:
            prev_item = self.treev_place.prev(cur_item)
            temp_text222 = self.treev_place.item(prev_item)['text']
            position222 = self.treev_place.item(prev_item)['values'][1]+1
            temp_values222 = self.treev_place.item(prev_item)['values'][0], position222 
        except:
            return
        temp_text = self.treev_place.item(cur_item)["text"]
        temp_values = self.treev_place.item(cur_item)["values"]
        position = temp_values[-1]-2
        new_child=self.treev_place.insert("", position, text=temp_text, values=(temp_values[0], position+1))
        self.treev_place.delete(cur_item)
        self.treev_place.insert("", position222, text=temp_text222, values=temp_values222)
        self.treev_place.delete(prev_item)
        self.treev_place.focus(new_child)
        self.treev_place.selection_set(new_child)

    # تابعی برای این که بشه اولویت نمایش یک مکان رو پایین آورد
    def down_tree_place(self):
        cur_item = self.treev_place.focus()
        try:
            next_item = self.treev_place.next(cur_item)
            temp_text222 = self.treev_place.item(next_item)['text']
            position222 = self.treev_place.item(next_item)['values'][1]-2
            temp_values222 = self.treev_place.item(next_item)['values'][0], position222+1
        except:
            return
        temp_text = self.treev_place.item(cur_item)["text"]
        temp_values = self.treev_place.item(cur_item)["values"]
        position = temp_values[-1]
        self.treev_place.insert("", position222, text=temp_text222, values=temp_values222)
        self.treev_place.delete(next_item)
        new_child=self.treev_place.insert("", position, text=temp_text, values=(temp_values[0], position+1))
        self.treev_place.delete(cur_item)
        self.treev_place.focus(new_child)
        self.treev_place.selection_set(new_child)

    # تابعی برای این که اولویت مکان ها رو به صورتی که تعیین کردیم در دیتابیس ذخیره کنه
    def confirm_tree_place(self, event=None):
        try:
            for item in self.treev_place.get_children():
                item = self.treev_place.item(item)
                id=int(item['text'])
                order=int(item['values'][-1])
                result_message, _ = self.connection.change_places_order(id, order)
            if result_message=='ok':
                # self.show_places_of_this_part() برای این گذاشته بودم که اگه ترتیب مکان ها رو برای یک بخش عوض کردیم، خود به خود تو بخش اضافه کردن پارامتر هم عوضش کنه. ولی در عمل به نظرم جالب نبود. خلاصه گذاشتم اینجا که اگه لازم شد کامنت رو فقط بردارم. چون بعدا یادم نمیاد چه تابعی رو باید صدا کنم و کلی وقت میگیرفت. گذاشتم اینجا باشه ولی کامنتش کردم.
                msb.showinfo("پیام موفقیت", f"ترتیب مکان ها با موفقیت تغییر یافت")
                self.refresh_ui()
            else:
                msb.showerror("خطا", result_message)
                print(_)
        except UnboundLocalError:
            msb.showerror("خطا", f"ابتدا باید یک بخش را انتخاب کنید و مکان های آن را مرتب کنید. سپس روی دکمه تایید بزنید.")


    ########################################## all counter functions ##########################################
    # تابعی برای این که بشه اولویت نمایش یک پارامتر رو بالا برد
    def up_tree_all_counters(self):
        cur_item = self.treev_all_counters.focus()
        try:
            prev_item = self.treev_all_counters.prev(cur_item)
            temp_text222 = self.treev_all_counters.item(prev_item)['text']
            position222 = self.treev_all_counters.item(prev_item)['values'][-1]+1
            temp_values222 = *(self.treev_all_counters.item(prev_item)['values'][0:3]), position222
        except:
            return
        temp_text = self.treev_all_counters.item(cur_item)["text"]
        temp_values = self.treev_all_counters.item(cur_item)["values"]
        position = temp_values[-1]-2
        new_child=self.treev_all_counters.insert("", position, text=temp_text, values=(*(temp_values[0:3]), position+1))
        self.treev_all_counters.delete(cur_item)
        self.treev_all_counters.insert("", position222, text=temp_text222, values=temp_values222)
        self.treev_all_counters.delete(prev_item)
        self.treev_all_counters.focus(new_child)
        self.treev_all_counters.selection_set(new_child)

    # تابعی برای این که بشه اولویت نمایش یک پارامتر رو پایین آورد
    def down_tree_all_counters(self):
        cur_item = self.treev_all_counters.focus()
        try:
            next_item = self.treev_all_counters.next(cur_item)
            temp_text222 = self.treev_all_counters.item(next_item)['text']
            position222 = self.treev_all_counters.item(next_item)['values'][-1]-2
            temp_values222 = *(self.treev_all_counters.item(next_item)['values'][0:3]), position222+1
        except:
            return
        temp_text = self.treev_all_counters.item(cur_item)["text"]
        temp_values = self.treev_all_counters.item(cur_item)["values"]
        position = temp_values[-1]
        self.treev_all_counters.insert("", position222, text=temp_text222, values=temp_values222)
        self.treev_all_counters.delete(next_item)
        new_child=self.treev_all_counters.insert("", position, text=temp_text, values=(*(temp_values[0:3]), position+1))
        self.treev_all_counters.delete(cur_item)
        self.treev_all_counters.focus(new_child)
        self.treev_all_counters.selection_set(new_child)

    # تابعی برای این که اولویت مکان ها رو به صورتی که تعیین کردیم در دیتابیس ذخیره کنه
    def confirm_tree_all_counters(self, event=None):
        for item in self.treev_all_counters.get_children():
            item = self.treev_all_counters.item(item)
            id=int(item['text'])
            order=int(item['values'][-1])
            result_message, _ = self.connection.change_parameters_order(id, order)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"ترتیب کنتور ها با موفقیت تغییر یافت")
            self.refresh_ui()
        else:
            msb.showerror("خطا", result_message)
            print(_)

    def refresh_all_counters_treeview(self):
        self.treev_all_counters.delete(*self.treev_all_counters.get_children())
        counters = self.connection.get_all_parameters_short_info()
        for i, counter in enumerate(counters):
            self.treev_all_counters.insert("", i, text=counter[0], values=(*(counter[1:]), i+1))

    ######################################### add statistics functions ######################################
    # تابعی برای این که تب های درون قسمت آمار پارامتر ها رو مقداردهی کنه
    def seed_tabs_of_parts(self):
        global all_counter_widgets
        all_counter_widgets = {}
        self.all_parts=self.connection.get_all_parts() # یک لیست تک بعدی از کل بخش ها
        self.all_parts.reverse() # خودش گفته بود که ترتیب از راست به چپ بشه به خاطر همین ریورس کردم اینجا. دقت کنم که جاش همین جاست. اگه بعدا ریورس کنم، اطلاعات رو اشتباه مینویسه.
        self.all_places = [] # یک لیست دو بعدی از کل مکان ها. تو لایه اول بخش ها هستند و لایه دوم، مکان های اون بخش.
        for part in self.all_parts:
            temp_places=self.connection.get_all_places_by_part_id(part.id)
            self.all_places.append(temp_places)
        self.all_counters_2d = [] # لیست دو بعدی از تمام کنتور ها برای ارسال به پارت ویجت که تمام کنتورهای یک بخش رو بسازه. دو بعدی هست. دقت کنم که بعضی از لیست هاش هم خالی هستند. چون بخشی هست که ممکنه کنتوری نداشته باشه.
        for places in self.all_places: # آل پلیسس یه لیست از مکان های هر بخش هست. پس روش دوباره حلقه میزنیم
            for place in places:
                self.all_counters_2d.append(self.connection.get_all_parameters_of_this_part_and_place(part_id=place.part_id, place_id=place.id))
        tabs_list = []
        parts_tab = []
        for i, part in enumerate(self.all_parts):
            tabs_list.append(Frame(self.tab_control_frame))
            tabs_list[i].pack()
            self.tab_control_frame.add(tabs_list[i], text =f'{part.title}')
            places_with_counters = []
            for place in self.all_places[i]:
                counters = self.connection.get_all_parameters_of_this_part_and_place(part_id=place.part_id, place_id=place.id)
                places_with_counters.append(counters)
            parts_tab.append(PartWidget(self.connection, tabs_list[i], places_with_counters, self))
            parts_tab[i].pack()
        self.tab_control_frame.pack(expand=1, fill="both")
        self.tab_control_frame.select(len(self.tab_control_frame.children)-1)
        for i, counter_widget in enumerate(list(all_counter_widgets.values())):
            counter_widget: CounterWidget
            if counter_widget.type==PARAMETER_TYPES[2]:
                pass # چون اصلا نمیشه روش اینتر زد.
            else:
                counter_widget.entry_workout.bind('<Return>', lambda e, i=i: self.goto_next_counter_widget(i)) # چون هر دو نوع ثابت و کنتور، این ویجت رو دارند و انتری هست.
                if counter_widget.type==PARAMETER_TYPES[0]: # نوع کنتور، یه انتری دیگه هم داره. پس اون رو هم بایند میکنیم.
                    counter_widget.entry_current_counter.bind('<Return>', lambda e, i=i: self.goto_next_counter_widget(i))

    def goto_next_counter_widget(self, index):
        global all_counter_widgets
        temp_all_counter_widgets = list(all_counter_widgets.values())
        length = len(temp_all_counter_widgets)
        for i in range(index+1, length):
            if i==length-1:
                self.btn_confirm_counter_log_insert.focus_set()
                self.btn_confirm_counter_log_update.focus_set()
                return
            if temp_all_counter_widgets[i].type==PARAMETER_TYPES[2]:
                continue
            elif temp_all_counter_widgets[i].type==PARAMETER_TYPES[1]:
                temp_all_counter_widgets[i].entry_workout.focus_set()
                temp_all_counter_widgets[i].entry_workout.select_range(0, 'end')
                return
            elif temp_all_counter_widgets[i].type==PARAMETER_TYPES[0]:
                if temp_all_counter_widgets[i].boolean_var_bad.get():
                    temp_all_counter_widgets[i].entry_workout.focus_set()
                    temp_all_counter_widgets[i].entry_workout.select_range(0, 'end')
                else:
                    temp_all_counter_widgets[i].entry_current_counter.focus_set()
                    temp_all_counter_widgets[i].entry_current_counter.select_range(0, 'end')
                return

    def disable_confirm_buttons(self, event=None):
        try:
            list(all_counter_widgets.values())[0].next()
        except:
            print('Unknown Expeption :D')
        self.btn_confirm_counter_log_insert.config(state='disabled', relief='flat')
        self.btn_confirm_counter_log_update.config(state='disabled', relief='flat')
        self.disable_for_safety()
    
    def disable_for_safety(self, event=None):
        global date_picker
        self.btn_refresh_counter_logs.config(state='disabled', relief='flat')
        date_picker.btn_yesterday.config(state='disabled', relief='flat')
        date_picker.btn_tomorrow.config(state='disabled', relief='flat')
        date_picker.btn_today.config(state='disabled', relief='flat')
        date_picker.combo_day.config(state='disabled')
        date_picker.combo_month.config(state='disabled')
        date_picker.combo_year.config(state='disabled')
    
    def enable_for_safety(self, event=None):
        global date_picker
        self.btn_refresh_counter_logs.config(state='normal', relief='raised')
        date_picker.btn_yesterday.config(state='normal', relief='raised')
        date_picker.btn_tomorrow.config(state='normal', relief='raised')
        date_picker.btn_today.config(state='normal', relief='raised')
        date_picker.combo_day.config(state='readonly')
        date_picker.combo_month.config(state='readonly')
        date_picker.combo_year.config(state='readonly')

    def enable_or_disable_confirm_button(self, event=None):
        global sheet_state
        part_name = self.tab_control_frame.tab(self.tab_control_frame.select(), "text")
        if part_name in self.logged_parts_names:
            sheet_state = 'update'
        else:
            sheet_state = 'insert'
        if sheet_state=='update':
            self.btn_confirm_counter_log_update.config(state='normal', relief='raised')
            self.btn_confirm_counter_log_insert.pack_forget()
            self.btn_confirm_counter_log_update.pack(side=LEFT, padx=PADX)
        else:
            self.btn_confirm_counter_log_update.pack_forget()
            self.btn_confirm_counter_log_insert.pack(side=LEFT, padx=PADX)
            self.btn_confirm_counter_log_insert.config(state='normal', relief='raised')

    def set_logged_parts_names(self):
        global date_picker
        self.logged_parts_names.clear()
        # for part in self.all_parts:
        #     part: Part
        #     last_log_date = self.connection.get_last_log_date_of_part_by_part_id(part.id)
        #     if last_log_date!=None and date_picker.get_date()<=last_log_date:
        #         self.logged_parts_names.add(part.title)
        # این کوئری بالا چون جوین کرده بودم هر بار 0.127 ثانیه تقریبا طول میکشید که خب برای ۵ تا بخش
        # میشد تقریبا 0.7 ثانیه و عملا کند تر میشد. به خاطر همین برگردوندمش به حالت قبلی که تو ورک بنچ
        # مینوشتم 0.000 ثانیه طول کشیده. چون جوین نکرده بودم. خلاصه گفتم اگه ۱۰۰ تا پارامتر هم باشه
        # همه با هم میشن 0.100 که باز هم سریعتر میشه. اما چون بخش همه شون یکی بود و با هم ثبت شده
        # بودند، اولی رو که گرفتم بریک گذاشتم. باز هم میشد ساده ترش کرد. اما ارزش وقت گذاشتن نداشت
        # به نظرم و خیلی سریعتر نمیشد. در حد زیر هزارم ثانیه
        for counters in self.all_counters_2d:
            for counter in counters:
                counter: Parameter
                last_log = self.connection.get_last_log_of_parameter_by_id(counter.id)
                if last_log!=None and date_picker.get_date()<=last_log:
                    self.logged_parts_names.add(counter.part_title)
                break

    def confirm_log_insert(self, event=None):
        global sheet_state, date_picker, all_counter_widgets
        self.disable_confirm_buttons()
        if date_picker.get_date() == None:
            msb.showerror("خطا", "لطفا تاریخ را به درستی انتخاب کنید")
            self.btn_confirm_counter_log_insert.config(state='normal', relief='raised')
            self.enable_for_safety()
            return
        part_name = self.tab_control_frame.tab(self.tab_control_frame.select(), "text")
        result = self.precheck_before_confirm(part_name)
        if result==None:
            self.btn_confirm_counter_log_insert.config(state='normal', relief='raised')
            self.enable_for_safety()
            return
        message = "لطفا یک بار دیگر به دقت اطلاعات را بررسی نمایید\n"
        message += "با انتخاب دکمه تایید، تمامی اطلاعات این بخش در دیتابیس ذخیره میشوند\n"
        message += "در صورت اطمنیان، دکمه تایید را فشار دهید"
        self.root.bell()
        answer = msb.askyesno("هشدار", message)
        if not answer:
            self.btn_confirm_counter_log_insert.config(state='normal', relief='raised')
            self.enable_for_safety()
            return
        for counter_widget in list(all_counter_widgets.values()):
            counter_widget: CounterWidget
            if counter_widget.part_title==part_name:
                if counter_widget.type in PARAMETER_TYPES[1:3]:
                    result_message, ـ = counter_widget.connection.create_parameter_log(counter_widget.workout, counter_widget.workout, 1, date_picker.get_date(), counter_widget.id, self.user.id)
                elif counter_widget.type==PARAMETER_TYPES[0]:
                    is_ok = 1 if counter_widget.boolean_var_bad.get()==False else 0
                    result_message, ـ = counter_widget.connection.create_parameter_log(counter_widget.b, counter_widget.workout, is_ok, date_picker.get_date(), counter_widget.id, self.user.id)
        if result_message == "ok":
            message = f"اطلاعات بخش {part_name} با موفقیت در دیتابیس اضافه شدند"
            msb.showinfo('success', message)
            sheet_state = 'update'
            self.btn_confirm_counter_log_insert.config(state='disabled', relief='flat')
            self.btn_confirm_counter_log_update.config(state='normal', relief='raised')
            self.btn_confirm_counter_log_insert.pack_forget()
            self.btn_confirm_counter_log_update.pack(side=LEFT, padx=PADX)
            self.enable_for_safety()
            try:
                list(all_counter_widgets.values())[0].next()
            except:
                msb.showinfo('دقت کنید', 'برای مشاهده تغییرات پارامترهای محاسباتی که به پارامترهای ثابت یا کنتورهای بخش های دیگر وابسته اند، ابتدا یک بار روی کنتورهای قابل نوشتن کلیک کنید که تغییرات آنها در برنامه اعمال شود و سپس روی تب مورد نظر خود کلیک کنید')
        else:
            self.fill_counter_widgets()
            msb.showerror("ارور", result_message)

    # تابی برای بررسی این که اعداد با ظاهر فعلی در صفحه در دیتابیس ذخیره شوند یا نه
    # اگر اشتباه باشند که اجازه نمیدهد. اگر منفی باشند کاربر باید تایید کند تا به مرحله بعد برود.
    def precheck_before_confirm(self, part_name):
        global all_counter_widgets
        negative_numbers = 0
        for counter_widget in list(all_counter_widgets.values()):
            counter_widget: CounterWidget
            if counter_widget.part_title==part_name:
                try:
                    if counter_widget.type==PARAMETER_TYPES[2]:
                        temp=float(counter_widget.entry_workout['text'])
                        if temp<0:
                            negative_numbers+=1
                    elif counter_widget.type==PARAMETER_TYPES[1]:
                        temp=float(counter_widget.entry_workout.get().strip())
                        if temp<0:
                            negative_numbers+=1
                    elif counter_widget.type==PARAMETER_TYPES[0]:
                        temp=float(counter_widget.entry_workout.get().strip())
                        if temp<0:
                            negative_numbers+=1
                        temp=float(counter_widget.entry_current_counter.get().strip())
                        if temp<0:
                            negative_numbers+=1
                except:
                    msb.showerror("اخطار", "به مقادیر دقت کنید. ظاهرا برخی از مقادیر یا ثبت نشده اند و یا به درستی ثبت نشده اند")
                    return
        if negative_numbers>0:
            message = f"{negative_numbers} عدد از فیلدها منفی شده اند.\n"
            message += "لطفا اعداد را با دقت بیشتری وارد کنید"
            answer = msb.askretrycancel("هشدار", message)
            if not answer:
                return None
        return "ok"

    def confirm_log_update(self):
        global date_picker, all_counter_widgets
        self.disable_confirm_buttons()
        if date_picker.get_date() == None:
            msb.showerror("خطا", "لطفا تاریخ را به درستی انتخاب کنید")
            self.btn_confirm_counter_log_update.config(state='normal', relief='raised')
            self.enable_for_safety()
            return
        part_name = self.tab_control_frame.tab(self.tab_control_frame.select(), "text")
        result = self.precheck_before_confirm(part_name)
        if result==None:
            self.btn_confirm_counter_log_update.config(state='normal', relief='raised')
            self.enable_for_safety()
            return
        message = "لطفا یک بار دیگر به دقت اطلاعات را بررسی نمایید\n"
        message += "با انتخاب دکمه تایید، تمامی اطلاعات این بخش در دیتابیس ویرایش میشوند\n"
        message += "در صورت اطمنیان، دکمه تایید را فشار دهید"
        self.root.bell()
        answer = msb.askyesno("هشدار", message)
        if not answer:
            self.btn_confirm_counter_log_update.config(state='normal', relief='raised')
            self.enable_for_safety()
            return
        for counter_widget in list(all_counter_widgets.values()):
            counter_widget: CounterWidget
            if counter_widget.part_title==part_name:
                if counter_widget.type in PARAMETER_TYPES[1:3]:
                    result_message, ـ = counter_widget.connection.update_parameter_log(counter_widget.workout, counter_widget.workout, 1, date_picker.get_date(), counter_widget.id, self.user.id)
                elif counter_widget.type==PARAMETER_TYPES[0]:
                    is_ok = 1 if counter_widget.boolean_var_bad.get()==False else 0
                    result_message, ـ = counter_widget.connection.update_parameter_log(counter_widget.b, counter_widget.workout, is_ok, date_picker.get_date(), counter_widget.id, self.user.id)
        if result_message == "ok":
            message = f"اطلاعات بخش {part_name} با موفقیت در دیتابیس ویرایش شدند"
            msb.showinfo('success', message)
            self.btn_confirm_counter_log_update.config(state='normal', relief='raised')
            self.enable_for_safety()
            try:
                list(all_counter_widgets.values())[0].next()
            except:
                msb.showinfo('دقت کنید', 'برای مشاهده تغییرات پارامترهای محاسباتی که به پارامترهای ثابت یا کنتورهای بخش های دیگر وابسته اند، ابتدا یک بار روی کنتورهای قابل نوشتن کلیک کنید که تغییرات آنها در برنامه اعمال شود و سپس روی تب مورد نظر خود کلیک کنید')
            self.update_next_logs_if_necessary()

        else:
            self.fill_counter_widgets()
            msb.showerror("ارور", result_message)

    def update_next_logs_if_necessary(self):
        global all_counter_widgets, date_picker
        updated_logs = self.connection.get_parameters_log_by_date(date_picker.get_date())
        updated_next_logs = self.connection.get_parameters_next_log_by_date(date_picker.get_date())
        for counters in self.all_counters_2d:
            for counter in counters:
                counter: Parameter
                if counter.type==PARAMETER_TYPES[2]:
                    parameters = get_formula_parameters(counter.formula)
                    values = []
                    for p in parameters:
                        if updated_next_logs.get(counter.variable_name)!=None:
                            # if p=='b':  نباید باشه. معامله به هم میریزه کلا این طوری.
                            #     values.append(float(updated_next_logs.get(counter.variable_name).value))
                            if p=='a':
                                values.append(float(updated_logs.get(counter.variable_name).workout))
                            else:
                                values.append(float(updated_next_logs.get(p).workout))
                        elif updated_next_logs.get(counter.variable_name)==None:
                            values.append(0.0)
                    answer = calculate_fn(counter.formula, parameters, values)
                    if updated_next_logs.get(counter.variable_name)!=None:
                        updated_next_logs[counter.variable_name].workout=answer
                elif counter.type==PARAMETER_TYPES[1]:
                    continue # پارامترهای ثابت، وابسته به بقیه نیستند. پس تغییری نمیکنند و لازم نیست الکی بررسیشون کنیم و چون تغییر نمیکنند به دیتابیس هم لازم نیست دستوری بدیم پس میریم سراغ پارامتر بعدی
                elif counter.type==PARAMETER_TYPES[0]:
                    parameters = get_formula_parameters(counter.formula)
                    values = []
                    for p in parameters:
                        if updated_next_logs.get(counter.variable_name)!=None:
                            if p=='b':
                                values.append(float(updated_next_logs.get(counter.variable_name).value))
                            elif p=='a':
                                values.append(float(updated_logs.get(counter.variable_name).value))
                            else:
                                values.append(float(updated_next_logs.get(p).workout))
                        elif updated_next_logs.get(counter.variable_name)==None:
                            values.append(0.0)
                    answer = calculate_fn(counter.formula, parameters, values)
                    if updated_next_logs.get(counter.variable_name)!=None:
                        # پارامترهای کنتور، اگه سالم باشن باید تغییر کنند. اما اگه خراب باشن، به مقدار ورک اوتشون دست نمیزنیم و همون قبلی میمونن
                        if updated_next_logs[counter.variable_name].is_ok:
                            updated_next_logs[counter.variable_name].workout=answer
        for log in updated_next_logs.values():
            log: ParameterLog
            if log!=None:
                if log.type==PARAMETER_TYPES[2]:
                    self.connection.change_log_by_computer_id(log)
                elif log.type==PARAMETER_TYPES[1]:
                    pass
                elif log.type==PARAMETER_TYPES[0]:
                    self.connection.change_log_by_computer_id(log)
        del updated_logs
        del updated_next_logs

    ########################################### generic functions ###########################################
    def select_color(self, what_color):
        choosed_color = colorchooser.askcolor()
        hex_color = choosed_color[1]
        if hex_color!=None:
            COLORS[what_color]=hex_color
        if what_color=='BG':
            self.btn_set_theme_bg_color.config(bg=hex_color)
            self.btn_set_theme_fg_color.config(bg=hex_color)
        elif what_color=='FG':
            self.btn_set_theme_bg_color.config(fg=hex_color)
            self.btn_set_theme_fg_color.config(fg=hex_color)
        elif what_color=='ALARM_COLOR':
            self.btn_set_theme_alarm_color.config(fg=hex_color, bg=hex_color)
        elif what_color=='WARNING_COLOR':
            self.btn_set_theme_warning_color.config(fg=hex_color, bg=hex_color)
        elif what_color=='OK_COLOR':
            self.btn_set_theme_ok_color.config(fg=hex_color, bg=hex_color)
        elif what_color=='DISABLED_BG':
            self.btn_set_theme_disabled_bg_color.config(fg=hex_color, bg=hex_color)
        elif what_color=='DISABLED_FG':
            self.btn_set_theme_disabled_fg_color.config(fg=hex_color, bg=hex_color)
        elif what_color=='BG_LIGHTER':
            self.btn_set_theme_bg_lighter_color.config(fg=hex_color, bg=hex_color)
        elif what_color=='FG2':
            self.btn_set_theme_fg2_color.config(fg=hex_color, bg=hex_color)

    def confirm_theme_color(self):
        try:
            os.mkdir('files')
        except FileExistsError:
            pass # فولدر خودش وجود داره. چی بهتر از این :)
        try:
            f = open(r'files/theme.json', 'w')
            dump(COLORS, f, indent=4)
            f.close()
            msb.showinfo('موفقیت', 'تم برنامه با موفقیت تغییر کرد. جهت استفاده از تم جدید برنامه را بسته و مجددا آغاز کنید')
        except:
            print('Error in openning file or while working with file :)')

    def refresh_ui(self):
        if self.connection.user.access_level==1:
            self.refresh_parts_tree_view()
            self.refresh_parts_values_in_comboboxes()
            # self.refresh_places_tree_view() # این ورودی میخواد. به خاطر همین کامنت کردم. گذاشتم که بعدا اشتباهی دوباره نذارمش.
            self.refresh_places_frame_after_selecting_part()
            self.refresh_all_counters_treeview()
        self.fill_counter_widgets()

    def refresh_ui_from_anywhere(self):
        global signal
        # sleep(1.2)
        while True:
            sleep(0.01)
            if signal:
                signal=0
                self.refresh_ui()
    
    def enable_btns_without_filling_counter_widgets(self, event=None):
        self.disable_for_safety()
        self.enable_or_disable_confirm_button()
        self.enable_for_safety()

    def fill_counter_widgets(self, event=None):
        global all_counter_widgets, sheet_state, date_picker
        self.btn_confirm_counter_log_insert.config(state='disabled', relief='flat')
        self.btn_confirm_counter_log_update.config(state='disabled', relief='flat')
        self.disable_for_safety()
        self.set_logged_parts_names()
        self.enable_or_disable_confirm_button()
        self.enable_for_safety()
        for counter_widget in list(all_counter_widgets.values()):
            counter_widget: CounterWidget
            if counter_widget.type == PARAMETER_TYPES[2]:
                counter_widget.entry_workout.config(bg=COLORS['ALARM_COLOR'])
            else:
                counter_widget.entry_workout.config(bg=COLORS['ALARM_COLOR'], readonlybackground=COLORS['ALARM_COLOR'])
            counter_widget.counter_log = counter_widget.connection.get_parameter_log_by_parameter_id_and_date(counter_widget.id, date_picker.get_date())
            if counter_widget.counter_log!=None:
                counter_widget.workout = counter_widget.counter_log.workout
                counter_widget.b = counter_widget.counter_log.value
            else:
                counter_widget.workout = 0
                counter_widget.b = 0
            counter_widget.a = counter_widget.connection.get_previous_value_of_parameter_by_id_and_date(counter_widget.id, date_picker.get_date())
            if counter_widget.a==None:
                counter_widget.a=0
            if sheet_state=='update':
                if counter_widget.type==PARAMETER_TYPES[2]:
                    counter_widget.label_previous_counter.config(text=round4(counter_widget.a))
                    counter_widget.entry_workout.config(text=round4(counter_widget.workout))
                elif counter_widget.type==PARAMETER_TYPES[1]:
                    counter_widget.entry_workout.delete(0, END)
                    counter_widget.entry_workout.insert(0, round4(counter_widget.workout))
                elif counter_widget.type==PARAMETER_TYPES[0]:
                    counter_widget.label_previous_counter.config(text=round4(counter_widget.a))
                    counter_widget.entry_current_counter.delete(0, END)
                    counter_widget.entry_current_counter.insert(0, round4(counter_widget.b))
                    counter_widget.entry_workout.config(state='normal')
                    counter_widget.entry_workout.delete(0, END)
                    counter_widget.entry_workout.insert(0, round4(counter_widget.workout))
                    if counter_widget.counter_log and counter_widget.counter_log.is_ok==0: # قبل از اند اون رو گذاشتم چون اگه رکوردی نبود نان میداد و خب نمیشه از تو هیچی ایز اوکی رو در آورد.
                        counter_widget.boolean_var_bad.set(True)
                        # counter_widget.entry_workout.config(state='normal') اضافیه. چند خط قبل نرمالش کردیم
                    elif counter_widget.counter_log:
                        counter_widget.boolean_var_bad.set(False)
                        counter_widget.entry_workout.config(state='disabled')
            elif sheet_state=='insert':
                if counter_widget.type==PARAMETER_TYPES[2]:
                    counter_widget.label_previous_counter.config(text=round4(counter_widget.b)) # inja
                    counter_widget.entry_workout.config(text='', bg=COLORS['ALARM_COLOR'])
                elif counter_widget.type==PARAMETER_TYPES[1]:
                    counter_widget.entry_workout.delete(0, END)
                    if counter_widget.default_value==DEFAULT_VALUES[0]:
                        counter_widget.entry_workout.insert(0, round4(counter_widget.workout))
                    elif counter_widget.default_value==DEFAULT_VALUES[1]:
                        counter_widget.entry_workout.insert(0, round4(DEFAULT_VALUES[1]))
                    elif counter_widget.default_value==DEFAULT_VALUES[2]:
                        pass
                elif counter_widget.type==PARAMETER_TYPES[0]:
                    counter_widget.label_previous_counter.config(text=round4(counter_widget.b)) # inja
                    counter_widget.entry_current_counter.delete(0, END)
                    if counter_widget.default_value==DEFAULT_VALUES[0]:
                        counter_widget.entry_current_counter.insert(0, round4(counter_widget.b))
                    elif counter_widget.default_value==DEFAULT_VALUES[1]:
                        counter_widget.entry_current_counter.insert(0, DEFAULT_VALUES[1])
                    elif counter_widget.default_value==DEFAULT_VALUES[2]:
                        pass
                    counter_widget.entry_workout.config(state='normal', disabledbackground=COLORS['ALARM_COLOR'])
                    counter_widget.entry_workout.delete(0, END)
                    counter_widget.entry_workout.config(state='disabled')
                    counter_widget.boolean_var_bad.set(False)
            try:
                create_tool_tip(counter_widget.lbl_info, text=counter_widget.counter_log.users_full_name)
            except:
                pass
        self.check_colors_and_correct_them()
    
    def check_colors_and_correct_them(self):
        global all_counter_widgets
        for counter_widget in list(all_counter_widgets.values()):
            counter_widget: CounterWidget
            counter_widget.check_color()

    def confirm_default_date(self):
        self.user.default_date=self.entry_set_default_date.get().strip()
        result_message, result = self.connection.update_default_date_of_user()
        if result_message == "ok":
            msb.showinfo("پیام موفقیت", f"تاریخ پیش فرض با موفقیت تغییر کرد")
        else:
            msb.showerror("ارور", result_message)
    
class DatePicker(MyWindows):
    days_list = [i for i in range(1, 32)]
    months_list = [i for i in range(1, 13)]
    years_list = [i for i in range(1350, 1451)]
    def __init__(self, connection: Connection, root: Tk):
        super().__init__(connection, root)
        global date_picker
        self.img_calendar       = Image.open(r'icons/calendar.png')
        self.img_previous_day   = Image.open(r'icons/right.png')
        self.img_next_day       = Image.open(r'icons/left.png')
        self.img_today          = Image.open(r'icons/today.png')
        self.img_calendar       = self.img_calendar     .resize((DATE_PICKER_ICON_SIZE, DATE_PICKER_ICON_SIZE))
        self.img_previous_day   = self.img_previous_day .resize((CHANGE_DAY_ICON_SIZE, CHANGE_DAY_ICON_SIZE))
        self.img_next_day       = self.img_next_day     .resize((CHANGE_DAY_ICON_SIZE, CHANGE_DAY_ICON_SIZE))
        self.img_today          = self.img_today        .resize((CHANGE_DAY_ICON_SIZE, CHANGE_DAY_ICON_SIZE))
        self.img_calendar       = ImageTk.PhotoImage(self.img_calendar)
        self.img_previous_day   = ImageTk.PhotoImage(self.img_previous_day)
        self.img_next_day       = ImageTk.PhotoImage(self.img_next_day)
        self.img_today          = ImageTk.PhotoImage(self.img_today)
        self.frame_right = Frame(self.frame, bg=COLORS['BG'])
        self.frame_middle = Frame(self.frame, bg=COLORS['BG'])
        self.frame_left = Frame(self.frame, bg=COLORS['BG'])
        self.frame_right.pack(side=RIGHT)
        self.frame_middle.pack(side=RIGHT, expand=True, fill='both')
        self.frame_left.pack(side=RIGHT, expand=True, fill='both')
        self.year = StringVar(self.frame_right)
        self.month = StringVar(self.frame_right)
        self.day = StringVar(self.frame_right)

        self.btn_show_date_picker = Button(self.frame_right, image=self.img_calendar, cnf=CNF_BTN, font=FONT3, padx=0, pady=0, command=self.show_or_hide_date_picker)
        self.combo_year = ttk.Combobox(self.frame_right, values=self.years_list, textvariable=self.year, width=7, state='readonly', font=FONT, justify='center')
        self.combo_month = ttk.Combobox(self.frame_right, values=self.months_list, textvariable=self.month, width=5, state='readonly', font=FONT, justify='center')
        self.combo_day = ttk.Combobox(self.frame_right, values=self.days_list, textvariable=self.day, width=5, state='readonly', font=FONT, justify='center')
        self.btn_today = Button(self.frame_right, image=self.img_today, cnf=CNF_BTN, font=FONT, padx=0, pady=0, command=lambda: self.refresh_date())
        self.combo_year.bind("<<ComboboxSelected>>", self.check_date)
        self.combo_month.bind("<<ComboboxSelected>>", self.check_date)
        self.combo_day.bind("<<ComboboxSelected>>", self.check_date)
        self.btn_show_date_picker.pack(cnf=CNF_PACK2)

        self.btn_yesterday = Button(self.frame_middle, image=self.img_previous_day, cnf=CNF_BTN, font=FONT, padx=0, pady=0, command=lambda: date_picker.time_delta(-1))
        self.btn_tomorrow = Button(self.frame_middle, image=self.img_next_day, cnf=CNF_BTN, font=FONT, padx=0, pady=0, command=lambda: date_picker.time_delta(1))
        self.label_date = Label(self.frame_middle, text=INVALID_DATE, cnf=CNF_LABEL, pady=32, width=14)
        self.btn_tomorrow.pack(cnf=CNF_PACK2, side=LEFT)
        self.label_date.pack(cnf=CNF_PACK2, side=LEFT)
        self.btn_yesterday.pack(cnf=CNF_PACK2, side=LEFT)
        self.refresh_date()

    def show_or_hide_date_picker(self):
        if self.btn_show_date_picker['relief']=='raised':
            self.btn_show_date_picker.config(relief='sunken')
            self.combo_day.pack(cnf=CNF_PACK2)
            self.combo_month.pack(cnf=CNF_PACK2)
            self.combo_year.pack(cnf=CNF_PACK2)
            self.btn_today.pack(cnf=CNF_PACK2)
        else:
            self.btn_show_date_picker.config(relief='raised')
            self.combo_day.pack_forget()
            self.combo_month.pack_forget()
            self.combo_year.pack_forget()
            self.btn_today.pack_forget()

    def refresh_date(self, date=None):
        if date==None: # این برای اول کار هست. وقتی که تابع تایم دلتا این رو صدا میکنه بهش روز رو میده و نان نیست. پس این ایف اجرا نمیشه.
            date=get_jnow()
            if self.connection.user.default_date==DEFAULT_DATE_VALUES[0]:
                d = jdatetime.timedelta(days=-1)
            else:
                d = jdatetime.timedelta(days=0)
            date = date+d
        self.combo_year.config(state='normal')
        self.combo_month.config(state='normal')
        self.combo_day.config(state='normal')
        self.combo_year.delete(0, END)
        self.combo_month.delete(0, END)
        self.combo_day.delete(0, END)
        self.combo_year.insert(0, date.year)
        self.combo_month.insert(0, date.month)
        self.combo_day.insert(0, date.day)
        self.combo_year.config(state='readonly')
        self.combo_month.config(state='readonly')
        self.combo_day.config(state='readonly')
        self.check_date()

    def check_date(self, event=None):
        global signal
        y = int(self.year.get())
        m = int(self.month.get())
        d = int(self.day.get())
        now = datetime.now()
        jalali_now = jdatetime.GregorianToJalali(now.year, now.month, now.day)
        if y>jalali_now.jyear:
            temp=INVALID_DATE
            self.label_date.config(text=temp)
            return
        if y==jalali_now.jyear and m>jalali_now.jmonth:
            temp=INVALID_DATE
            self.label_date.config(text=temp)
            return
        if y==jalali_now.jyear and m==jalali_now.jmonth and d>jalali_now.jday:
            temp=INVALID_DATE
            self.label_date.config(text=temp)
            return
        try:
            date = jdatetime.date(int(y), int(m), int(d))
            temp = f"{WEEKDAYS.get(date.weekday())} {d} {MONTH_NAMES.get(int(m))} {y}"
            self.label_date.config(text=temp)
            print(self.get_date())
            signal=1
        except ValueError:
            temp=INVALID_DATE
            self.label_date.config(text=temp)

    def time_delta(self, days):
        try:
            now = datetime.now()
            jdate = jdatetime.datetime(int(self.combo_year.get()), int(self.combo_month.get()), int(self.combo_day.get()), now.hour, now.minute, now.second)
            d = jdatetime.timedelta(days=days)
            new_date = jdate + d
            self.refresh_date(new_date)
        except ValueError:
            msb.showerror('', INVALID_DATE)

    def get_date(self):
        if self.label_date['text']==INVALID_DATE:
            jdate = get_jnow()
            jdate = jdatetime.date(year=jdate.year, month=jdate.month, day=jdate.day)
            date = jdate.togregorian()
            return date
        try:
            jdate = jdatetime.date(int(self.combo_year.get()), int(self.combo_month.get()), int(self.combo_day.get()))
            date = jdate.togregorian()
            return date
        except:
            return None
        

class PartWidget(MyWindows):
    def __init__(self, connection: Connection, root: Tk, places_with_counters, staff_window: StaffWindow):
        super().__init__(connection, root)
        global all_counter_widgets
        self.places_with_counters=places_with_counters # یک لیستی از مکان ها با پارامترهایی که داخلشون هست. یعنی یک لیستی از تاپل ها که هر کودوم از تاپل ها هر عضوشون یه پارامتر هست.
        self.staff_window = staff_window
        self.my_canvas = Canvas(self.frame, width=int(self.S_WIDTH*0.985), height=int(self.S_HEIGHT*0.72), bg=COLORS['BG'])
        self.my_canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.ver_scrollbar = Scrollbar(self.frame, orient=VERTICAL, command=self.my_canvas.yview)
        self.hor_scrollbar = Scrollbar(self.frame, orient=HORIZONTAL, command=self.my_canvas.xview)
        self.my_canvas.configure(yscrollcommand=self.ver_scrollbar.set, xscrollcommand=self.hor_scrollbar.set)
        self.my_canvas.grid(row=1, column=1, sticky='news')
        # self.bg_pic = Image.open(r'icons/bg_pic.png')
        # self.bg_pic.putalpha(127)
        # self.bg_pic = self.bg_pic.resize((self.S_WIDTH, self.S_HEIGHT))
        # self.bg_pic = ImageTk.PhotoImage(self.bg_pic)
        # self.label_background = Label(self.my_canvas, image=self.bg_pic)
        # self.label_background.place(x=0, y=0, width=self.S_WIDTH, height=self.S_HEIGHT)
        self.ver_scrollbar.grid(row=1, column=3, sticky='ns')
        self.hor_scrollbar.grid(row=2, column=1, columnspan=3, sticky='ew')
        self.my_canvas.bind('<Configure>', lambda e: self.my_canvas.configure(scrollregion=self.my_canvas.bbox("all")))
        self.places_window = Frame(self.my_canvas, bg=COLORS['BG'])
        self.my_canvas.create_window((0, 0), window=self.places_window, anchor="ne")
        for i, counters in enumerate(self.places_with_counters):
            if counters: # یعنی اگر یک مکان پارامتر هایی داشت این کارها رو انجام بده اگه نداشت الکی ردیف براش درست نکنه
                self.frame_row = Frame(self.places_window, bg=COLORS['BG'])
                self.frame_row.bind("<MouseWheel>", self.on_mousewheel)
                for index in range(991, 1000):
                    self.frame_row.columnconfigure(index=index, weight=1, minsize=190)
                self.frame_row.columnconfigure(index=1000, weight=1, minsize=120)
                self.frame_row.grid(sticky='e')
                place_name=counters[0].place_title
                Label(self.frame_row, text=place_name, font=FONT2, bg=COLORS['BG'], fg=COLORS['FG'], width=WORDS_WIDTH//2).grid(row=i, column=1000, sticky='news', padx=4, pady=2)
                for j, counter in enumerate(counters):
                    counter: Parameter
                    c = CounterWidget(
                        self.connection,
                        self.frame_row,
                        part=counter.part,
                        place=counter.place,
                        name=counter.name,
                        variable_name=counter.variable_name,
                        formula=counter.formula,
                        type=counter.type,
                        default_value=counter.default_value,
                        unit=counter.unit,
                        warning_lower_bound=counter.warning_lower_bound,
                        warning_upper_bound=counter.warning_upper_bound,
                        alarm_lower_bound=counter.alarm_lower_bound,
                        alarm_upper_bound=counter.alarm_upper_bound,
                        id=counter.id,
                        place_title=counter.place_title,
                        part_title=counter.part_title,
                        )
                    all_counter_widgets[c.variable_name] = c
                    c.frame.bind("<MouseWheel>", self.on_mousewheel)
                    c.info_widget.bind("<MouseWheel>", self.on_mousewheel)
                    c.lbl_info.bind("<MouseWheel>", self.on_mousewheel)
                    c.lbl_title.bind("<MouseWheel>", self.on_mousewheel)
                    c.entry_workout.bind("<MouseWheel>", self.on_mousewheel)
                    try:
                        c.entry_current_counter.bind("<MouseWheel>", self.on_mousewheel)
                    except:
                        pass
                    try:
                        c.label_previous_counter.bind("<MouseWheel>", self.on_mousewheel)
                    except:
                        pass
                    try:
                        c.btn_copy.bind("<MouseWheel>", self.on_mousewheel)
                    except:
                        pass
                    try:
                        c.checkbutton_bad.bind("<MouseWheel>", self.on_mousewheel)
                    except:
                        pass
                    c.grid(row=i, column=1000-1-j, sticky='news', padx=4, pady=2)

    def on_mousewheel(self, event=None):
        x, y = win32api.GetCursorPos()
        x=self.ver_scrollbar.winfo_rootx()
        win32api.SetCursorPos((x+6, y))

class CounterWidget(Parameter, MyWindows):
    def __init__(self, connection: Connection, root: Tk, part, place, name, variable_name, formula='', type='کنتور', default_value=0, unit=None, warning_lower_bound=None, warning_upper_bound=None, alarm_lower_bound=None, alarm_upper_bound=None, id=None, place_title=None, part_title=None, *args, **kwargs):
        super().__init__(part, place, name, variable_name, formula, type, default_value, unit, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, id, place_title, part_title)
        MyWindows.__init__(self, connection, root)
        self.img_copy = Image.open(r'icons/copy.png')
        self.img_copy = self.img_copy.resize((COPY_ICON_SIZE, COPY_ICON_SIZE))
        self.img_copy = ImageTk.PhotoImage(self.img_copy)
        self.info_widget = Frame(self.root, bg=COLORS['BG'])
        self.info_widget.grid()
        self.frame = LabelFrame(self.root, labelwidget=self.info_widget, cnf=CNF_LBL_FRM, padx=PADX, pady=PADY, labelanchor='n', bg=COLORS['BG'], fg=COLORS['FG'], *args, **kwargs)
        self.lbl_title = Label(self.info_widget, cnf=CNF_LABEL2, text=self.name)
        self.lbl_info = Label(self.info_widget, cnf=CNF_LABEL2, padx=1, text='🛈')
        self.lbl_title.grid(row=1, column=1)
        self.lbl_info.grid(row=1, column=2)
        self.counter_log = None # بعدا برای هر پارامتر مقدار دهی میشه با یک لاگ کامل از اون پارامتر. دیگه اینجا الکی به دیتابیس هیت نزدم
        # self.a = self.b = self.workout = None # این هم بعدا مقدار دهی میشه. اول کار تعریف کردم که ارور نده و در جاهای دیگه کد بدونه که هر نمونه از این کلاس این ۲ تا رو داره
        self.a = self.b = self.workout = 0
        if self.type==PARAMETER_TYPES[2]:
            self.label_previous_counter = Label(self.frame, cnf=CNF_LABEL2, *args, **kwargs)
            self.entry_workout = Label(self.frame, cnf=CNF_LABEL2, font=FONT2, pady=4, width=18, padx=14, height=1, *args, **kwargs)
        elif self.type==PARAMETER_TYPES[1]:
            self.btn_copy = Label(self.frame, image=self.img_copy, cnf=CNF_BTN2, relief='raised', *args, **kwargs)
            self.btn_copy.bind('<Button-1>', self.copy_paste)
            self.entry_workout = Entry(self.frame, cnf=CNF_ENTRY2, font=FONT2, width=23, *args, **kwargs)
            self.frame.bind('<FocusOut>', self.next)
            self.entry_workout.bind('<KeyRelease>', self.update_workout)
            self.btn_copy.grid(row=1, column=2, cnf=CNF_GRID2, padx=9)
        elif self.type==PARAMETER_TYPES[0]:
            self.btn_copy = Label(self.frame, image=self.img_copy, cnf=CNF_BTN2, relief='raised', *args, **kwargs)
            self.btn_copy.bind('<Button-1>', self.copy_paste)
            self.entry_current_counter = Entry(self.frame, cnf=CNF_ENTRY2, font=FONT2_5, width=WORDS_WIDTH2+2, *args, **kwargs)
            self.label_previous_counter = Label(self.frame, cnf=CNF_LABEL2, *args, **kwargs)
            self.entry_workout = Entry(self.frame, cnf=CNF_ENTRY2, font=FONT2, width=WORDS_WIDTH3+2, *args, **kwargs)
            self.boolean_var_bad = BooleanVar(self.frame)
            self.checkbutton_bad = Checkbutton(self.frame, cnf=CNF_CHB2, variable=self.boolean_var_bad, text='خرابی', command=self.check)
            self.frame.bind('<FocusOut>', self.next)
            self.entry_current_counter.bind('<KeyRelease>', self.update_workout)
            self.entry_workout.bind('<KeyRelease>', self.update_workout)
            self.btn_copy               .grid(row=1, column=3, cnf=CNF_GRID2)
            self.entry_current_counter  .grid(row=1, column=2, cnf=CNF_GRID2)
            self.checkbutton_bad        .grid(row=2, column=1, cnf=CNF_GRID2)
            self.label_previous_counter .grid(row=2, column=2, cnf=CNF_GRID2)
        self.entry_workout.grid(row=1, column=1, cnf=CNF_GRID2)
 
    def check_color(self, event=None):
        w_l = self.warning_lower_bound
        w_u = self.warning_upper_bound
        a_l = self.alarm_lower_bound
        a_u = self.alarm_upper_bound
        bg=COLORS['ALARM_COLOR'] # یه سری ارور میداد با این که ترای و اکسپت گذاشته بودم. خلاصه حالتی پیش میومد که میگفت بی جی تعریف شده نیست.
        # من هم گفتم اول کار میذارم رنگش آلارم باشه. اگه تغییر کرد که خب درست میشه. اگه نکرد که خب تعریف شده و قرمز هست بهم ارور نمیده دیگه
        # باز هم ارور میداد. فکر کنم به خاطر تب هایی
        # هست که از بین رفتن. اما چون داخل ترای نوشتم برنامه درست کار میکنه. فعلا گفتم روش وقت نذارم.
        try:
            if self.type == PARAMETER_TYPES[2]:
                self.workout = float(self.entry_workout['text'])
            else:
                self.workout = float(self.entry_workout.get())
            if self.type == PARAMETER_TYPES[0] and self.boolean_var_bad.get()==False:
                float(self.entry_current_counter.get()) # کاری باهاش ندارم. فقط الکی گرفتم که اگه مقدار فلوت نداشت ارور بده و باعث شه قرمز شه. دقت کنم که اولش هم چک کردم که مدلش کنتور باشه که بولین ور رو داشته باشه. اگه مدل کنتور نباشه که خب ورک اوت رو برای همه دارم چک میکنم در ادامه. 
            if isinstance(a_l, Decimal) and self.workout<a_l:
                bg = COLORS['ALARM_COLOR']
            elif isinstance(w_l, Decimal) and self.workout<w_l:
                bg = COLORS['WARNING_COLOR']
            elif isinstance(a_u, Decimal) and self.workout>a_u:
                bg = COLORS['ALARM_COLOR']
            elif isinstance(w_u, Decimal) and self.workout>w_u:
                bg = COLORS['WARNING_COLOR']
            else:
                bg = COLORS['OK_COLOR']
        except ValueError:
            bg=COLORS['ALARM_COLOR']
        except TypeError:
            bg=COLORS['ALARM_COLOR']
        finally:
            if self.type==PARAMETER_TYPES[0]:
                if self.boolean_var_bad.get():
                    self.entry_workout.config(state='normal', bg=bg)
                    self.checkbutton_bad.config(fg=COLORS['ALARM_COLOR'])
                else:
                    self.entry_workout.config(state='disabled', disabledbackground=bg)
                    self.checkbutton_bad.config(fg=COLORS['FG'])
            else:
                self.entry_workout.config(state='normal', bg=bg)
          
    def next(self, event=None):
        for _ in range(6):
            if self.type==PARAMETER_TYPES[2]: # نمیتونه باشه. نوشتم که بدونم بررسی شده. رو محاسباتی ها نمیشه اینتر زد.
                self.a = float(self.label_previous_counter['text'])
            elif self.type==PARAMETER_TYPES[1]:
                try:
                    self.workout = float(self.entry_workout.get().strip())
                except ValueError:
                    self.workout = 0
                except TypeError:
                    self.workout = 0
                self.check_color()
            elif self.type==PARAMETER_TYPES[0]:
                self.a = float(self.label_previous_counter['text'])
                try:
                    self.b = float(self.entry_current_counter.get().strip())
                except ValueError:
                    self.b = 0
                except TypeError:
                    self.b = 0
                self.check_color()
                try:
                    self.workout = float(self.entry_workout.get().strip())
                except ValueError:
                    self.workout = 0
                except TypeError:
                    self.workout = 0
                self.check_color()
            self.update_all_variables_current_value_and_workout()
    
    def update_all_variables_current_value_and_workout(self):
        global all_counter_widgets
        for counter_widget in list(all_counter_widgets.values()):
            counter_widget: CounterWidget
            if counter_widget.type==PARAMETER_TYPES[2]:
                parameters = get_formula_parameters(counter_widget.formula)
                values = []
                for p in parameters:
                    # تو فرمول محاسباتی نمیشه از مقدار امروز خودش استفاده کرد. تا بینهایت پیش میره. پس نباید باشه
                    # if p=='b':
                    #     values.append(counter_widget.b)
                    counter_widget.a=float(counter_widget.label_previous_counter['text'])
                    if p=='a':
                        values.append(float(counter_widget.a))
                    else:
                        temp:CounterWidget = all_counter_widgets.get(p)
                        if temp!=None:
                            values.append(float(temp.workout))
                        else:
                            values.append(0.0)
                counter_widget.workout = calculate_fn(counter_widget.formula, parameters, values)
                counter_widget.entry_workout.config(text=counter_widget.workout)
            elif counter_widget.type==PARAMETER_TYPES[1]:
                pass
                # لازم نیست کاری بکنیم. چون پارامترهای ثابت با تغییر بقیه تغییر نمیکنند.
                # اگر خودشون تغییر بکنند که همون لحظه تغییر میکنه
                # اما تغییر بقیه باعث تغییر پارامتر ثابت نمیشه. پس الکی بررسیش نمیکنیم.
            elif counter_widget.type==PARAMETER_TYPES[0]:
                if counter_widget.boolean_var_bad.get()==False:
                    parameters = get_formula_parameters(counter_widget.formula)
                    values = []
                    for p in parameters:
                        try:
                            counter_widget.b=float(counter_widget.entry_current_counter.get())
                        except ValueError:
                            counter_widget.b=0
                        counter_widget.a=float(counter_widget.label_previous_counter['text'])
                        if p=='b':
                            values.append(counter_widget.b)
                        elif p=='a':
                            values.append(counter_widget.a)
                        else:
                            temp:CounterWidget = all_counter_widgets.get(p)
                            if temp!=None:
                                values.append(float(temp.workout))
                            else:
                                values.append(0.0)
                    counter_widget.workout = calculate_fn(counter_widget.formula, parameters, values)
                    counter_widget.entry_workout.config(state='normal')
                    counter_widget.entry_workout.delete(0, END)
                    counter_widget.entry_workout.insert(0, counter_widget.workout)
                    counter_widget.entry_workout.config(state='readonly')
            counter_widget.check_color()

    def update_workout(self, event=None):
        global all_counter_widgets
        if event and event.keysym=='Return': # باگ داشت وقتی اینتر میزدیم آپدیت میشد. اما چون دکمه اینتر ول شده بود دوباره میومد این رو صدا میکرد و به هم میزد همون کنتور ویجت رو. به خاطر همین اینتر رو ازش حذف کردم که موقعی که انگشت رو از رو اینتر برداشتیم آپدیت نکنه.
            # حالا اگه رو دکمه کپی میزدیم هیچ ایونتی ارسال نمیشد و این ایف ارور میداد. پس گفتم اگه ایونتی وجود داشت و اینتر بود ریترن کن. در غیر این صورت کارت رو انجام بده.
            return
        if event and event.keysym=='period': # این حالت هم باگ داشت نمیشد داخل ورک اوت تو حالت خرابی نقطه گذاشت. روش های مختلف هر کودوم یه مدل اعصاب خرد کن بود و باگ جدید داشت. این مدل به نظرم کمترین باگ رو داشت اینجا گفتم ریترن کنه
            return
        if self.type==PARAMETER_TYPES[2]:
            self.a = float(self.label_previous_counter['text'])
        elif self.type==PARAMETER_TYPES[1]:
            # تو کنتورهای ثابت میشه مقدار نوشت. ممکنه مقدار اشتباه و یا کم و زیاد نوشته بشه. پس ممکنه ارور بده و باید بررسی بشه. رنگ هم باید بررسی بشه و در صورت لزوم تغییر کنه.
            try:
                self.workout=float(self.entry_workout.get().strip())
            except ValueError:
                self.workout=0
            except TypeError:
                self.workout=0
            self.check_color()
        elif self.type==PARAMETER_TYPES[0]:
            if self.boolean_var_bad.get():
                self.check_color()
            else:
                self.a = float(self.label_previous_counter['text'])
                try:
                    self.b = float(self.entry_current_counter.get().strip())
                except ValueError:
                    self.b=0
                except TypeError:
                    self.b=0
                parameters = get_formula_parameters(self.formula)
                values = []
                for p in parameters:
                    if p=='b':
                        values.append(float(self.b))
                    elif p=='a':
                        values.append(float(self.a))
                    else:
                        temp: CounterWidget = all_counter_widgets.get(p)
                        if temp!=None:
                            values.append(float(temp.workout))
                        else:
                            values.append(0.0)
                self.workout = calculate_fn(self.formula, parameters, values)
                self.entry_workout.config(state='normal')
                self.entry_workout.delete(0, END)
                self.entry_workout.insert(0, self.workout)
                self.entry_workout.config(state='disabled')
                self.check_color()
        self.next()
        # اینجا یه بار که تابع نکست رو کال میکردم خودش درست میشد. اما بقیه ها نه. باید رو یکی دیگه کلیک میکردم.
        # هاور هم گذاشتم باید دوبار ماوس رو میبردیم بیرون که خیلی جالب نبود.
        # بهترین راه حل به نظرم این بود که دو بار خودم نکست رو پشت سر هم صدا کنم که هم خودش همون لحظه آپدیت
        # بشه و هم کنتورهایی که بهش وابسته هستند.
        # وقتی پارامترهای بیشتری به هم وابسته شدند همین کار رو باید تکرار میکردیم. برای موردی که خودش گفته بود ۳ تا
        # کافی بود. خودم چند تا دیگه گذاشتم دیدم باز کار نمیکنه به خاطر همین ۶ بار کال کردم درست شد. برای محکم کاری
        # ۶ بار صداش کردم. اگه سرعت برنامه  کند شد هماهنگ کنم باهاش ببینم حداکثر چند بار لازمه که اضافه تکرارش نکنم.
        # نکته آخر این که وقتی با فوکس اوت جا به جا میشدیم هنوز این مشکل بود. به جای این که اونجا هم همین کار رو کنم، این حلقه 
        # رو داخل خود تابع نکست نوشتم که این تکرار رو انجام بده.

    def copy_paste(self, event=None):
        if self.type==PARAMETER_TYPES[2]:
            pass # هیچ وقت اتفاق نمیفته
        elif self.type==PARAMETER_TYPES[1]:
            self.entry_workout.delete(0, END)
            self.entry_workout.insert(0, round4(self.b))
        elif self.type==PARAMETER_TYPES[0]:
            self.entry_current_counter.delete(0, END)
            self.entry_current_counter.insert(0, self.label_previous_counter['text'])
        # درسته که ثابت ها فرمول ندارن. اما چون ممکنه بقیه رو تغییر بدن، تابع آپدیت ورک اوت رو در هر حالت
        # صدا میکنیم. چون توی اون بعد از تغییر خودشون، بقیه رو هم تغییر میدن.
        self.update_workout()
    
    def check(self):
        if self.type==PARAMETER_TYPES[0]: # اگه انواع دیگه باشن، بولین ور براشون تعریف نشده و این تابع براشون ارور میده. پس شرط گذاشتم براش.
            if self.boolean_var_bad.get():
                self.checkbutton_bad.config(fg=COLORS['ALARM_COLOR'])
                self.entry_workout.config(state='normal')
                self.entry_workout.focus_set()
            else:
                self.checkbutton_bad.config(fg=COLORS['FG'])
                self.entry_workout.config(state='readonly')
                self.entry_current_counter.focus_set()
            self.update_workout()


############################################### Stackoverflow ###############################################
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 30
        y = y + cy + self.widget.winfo_rooty() +20
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify='left',
                      background="#ffffe0", relief='solid', borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def create_tool_tip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
