from ui_settings import *
from PIL import Image, ImageTk
from connection import Connection
from functions import calculate_fn, get_formula_parameters, what_is_variable_name_problem, what_is_formula_problem, get_jnow, round3, jdatetime, datetime
from models import CounterLog, Part, Place, Staff, Counter
from ui_settings import Tk
from threading import Thread
from time import sleep
from decimal import Decimal

class MyWindows():
    def __init__(self, connection: Connection, root: Tk):
        self.connection = connection
        self.root = root
        self.frame = Frame(self.root, bg=BG)

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    # چون CounterWidget‌ ارث بری دوگانه از کنتور و این داره و کنتور ها متغیر place دارن. مشکل پیش میومد. اسم تابع place این رو عوض کردم که با اون به مشکل نخوره.
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
        self.entry_username.insert(0, 'admin')
        self.entry_password.insert(0, 'admin')
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
            self.entry_password.delete(0, END)
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
        global date_picker, signal
        self.is_staff_window_running = True # وقتی برمیگشتیم به صفحه ورود و دوباره وارد میشدیم، بعضی وقت ها ارور میداد و نفهمیدم دلیلش چی بود. اما به خاطر ترد قبلی بود که به خاطر وایل ترو زنده مونده بود. به خاطر همین این متغیر رو تعریف کردم که با اول کار میشه ترو و وقتی بک رو میزنیم مقدارش میشه فالس که خود به خود ترد کارش تموم بشه و نابود بشه. احتمالا چند باری که ارور نداد به خاطر گاربیج کالکتور بود که ترد بیخود رو حذف میکرد. اما خب همیشه این کار رو نمیکرد و این طوری چندین بار تست کردم ارور نداد. 
        signal = 0 # برای این که وقتی یه آپدیتی کردیم رو یه پارامتر، ظاهر برنامه رو رفرش کنیم و به تابع رفرش یو آی این کلاس دسترسی داشته باشیم.
        self.logged_parts_names = set() # یه لیست از پارت هایی که امروز لاگ رو ثبت کردند. البته اول لیست گرفته بودم. بعد گفتم مجموعه کنم بهتره. اگه ثبت کردند، اسمشون میره تو این مجموعه که دیگه نتونن ثبت کنن و فقط بتونن ویرایش کنن. اول کار هیچ کس ثبت نکرده، پس فقط یه مجموعه خالی داریم. هر بخشی که ثبت کرد وارد این مجموعه میشه و بعد از اون فقط میتونه ویرایش کنه.
        Thread(target=self.refresh_ui_from_anywhere, daemon=True).start()
        self.user = user
        self.main_window = Toplevel(self.frame)
        self.main_window.title(f'حساب کاربری {self.user}')
        self.main_window.config(bg=BG)
        # self.main_window.resizable(False, False)
        self.main_window.geometry('1380x900+400+0')
        # self.main_window.geometry(f"+{S_WIDTH//4}+0")
        self.main_window.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.tab_control = ttk.Notebook(self.main_window) 
        self.tab_control.pack(anchor='n')
        self.frame_change_password_tab = Frame(self.tab_control, bg=BG)
        self.frame_add_statistics_tab = Frame(self.tab_control, bg=BG)
        self.frame_set_default_date_tab = Frame(self.tab_control, bg=BG)
        self.tab_control.add(self.frame_change_password_tab, text ='تغییر رمز عبور')
        self.tab_control.add(self.frame_set_default_date_tab, text ='تاریخ پیش فرض')
        if self.user.access_level==1:
            self.frame_add_part_tab = Frame(self.tab_control, bg=BG)
            self.frame_add_place_tab = Frame(self.tab_control, bg=BG)
            self.frame_all_counters_tab = Frame(self.tab_control, bg=BG)
            self.frame_add_counter_tab = Frame(self.tab_control, bg=BG)
            self.frame_add_user_tab = Frame(self.tab_control, bg=BG)
            self.tab_control.add(self.frame_add_user_tab, text ='افزودن کاربر جدید')
            self.tab_control.add(self.frame_all_counters_tab, text ='پارامترهای موجود')
            self.tab_control.add(self.frame_add_counter_tab, text ='افزودن پارامتر جدید')
            self.tab_control.add(self.frame_add_place_tab, text ='افزودن مکان جدید')
            self.tab_control.add(self.frame_add_part_tab, text ='افزودن بخش جدید')
        self.tab_control.add(self.frame_add_statistics_tab, text ='ثبت آمار')
        self.tab_control.select(self.frame_add_statistics_tab)

        ###################################### frame_set_default_date ######################################
        self.frame_set_default_date = Frame(self.frame_set_default_date_tab, bg=BG)
        self.frame_set_default_date.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
        # self.frame_set_default_date.place(relx=0.36, rely=0.04, relwidth=1, relheight=1)
        self.label_set_default_date = Label(self.frame_set_default_date, text='تاریخ پیش فرض', cnf=CNF_LABEL)
        self.entry_set_default_date = ttk.Combobox(self.frame_set_default_date, values=DEFAULT_DATE_VALUES, font=FONT, width=WORDS_WIDTH, justify='center')
        self.entry_set_default_date.insert(0, DEFAULT_DATE_VALUES[0])
        self.entry_set_default_date.config(state='readonly')
        self.btn_set_default_date = Button(self.frame_set_default_date, text='تایید', cnf=CNF_BTN, font=FONT3, command=self.confirm_default_date)
        # self.btn_back_set_default_date = Button(self.frame_set_default_date, text='بازگشت به صفحه ورود', cnf=CNF_BTN, command=self.back)
        self.label_set_default_date.grid(row=1, column=3, cnf=CNF_GRID)
        self.entry_set_default_date.grid(row=1, column=2, cnf=CNF_GRID)
        self.btn_set_default_date.grid(row=1, column=1, cnf=CNF_GRID)
        # self.btn_back_set_default_date.grid(row=1, column=0, cnf=CNF_GRID)

        ###################################### frame_add_statistics ######################################
        self.frame_add_statistics = Frame(self.frame_add_statistics_tab, bg=BG)
        self.frame_add_statistics.pack(side=RIGHT, anchor='ne')
        self.date_picker_frame = Frame(self.frame_add_statistics, bg=BG)
        self.date_picker_frame.pack(side=TOP, expand=True, fill='x')
        self.tab_control_frame = ttk.Notebook(self.frame_add_statistics)
        self.tab_control_frame.pack(side=TOP, expand=True, fill='both')
        self.change_day_frame = Frame(self.frame_add_statistics, bg=BG)
        self.change_day_frame.pack(side=TOP, expand=True)
        # self.tab_control_frame.bind('<<NotebookTabChanged>>', self.enable_or_disable_confirm_button)
        # این خیلی ارور میداد اذیت میکرد عوضش کردم. کار میکرد برنامه اما واقعا خووندن ارورها و
        # دیباگ کردن رو خیلی سخت کرده بود. به جاش این سه تا بایند رو گذاشتم
        self.tab_control_frame.bind('<Button-1>', self.disable_confirm_button)
        self.tab_control_frame.bind('<Key>', self.disable_confirm_button)
        self.tab_control_frame.bind('<ButtonRelease-1>', self.enable_or_disable_confirm_button)
        date_picker = DatePicker(self.connection, self.date_picker_frame)
        date_picker.pack(side=RIGHT, expand=True, fill='both')
        self.btn_confirm_counter_log_insert = Button(self.date_picker_frame, text="ذخیره", state='disabled', font=FONT2, cnf=CNF_BTN, command=self.confirm_log_insert)
        self.btn_confirm_counter_log_insert.pack(side=LEFT, padx=PADX)
        self.btn_confirm_counter_log_update = Button(self.date_picker_frame, text="ویرایش", state='disabled', font=FONT2, cnf=CNF_BTN, command=self.confirm_log_update)
        self.btn_confirm_counter_log_update.pack(side=LEFT, padx=PADX)
        self.btn_yesterday = Button(self.change_day_frame, text='روز قبل', cnf=CNF_BTN, font=FONT3, padx=0, pady=0, command=lambda: date_picker.time_delta(-1))
        self.btn_tomorrow = Button(self.change_day_frame, text='روز بعد', cnf=CNF_BTN, font=FONT3, padx=0, pady=0, command=lambda: date_picker.time_delta(1))
        self.btn_yesterday.pack(cnf=CNF_PACK2)
        self.btn_tomorrow.pack(cnf=CNF_PACK2)
        self.seed_tabs_of_parts()

        ###################################### frame_change_users_password ######################################
        self.frame_change_users_password = Frame(self.frame_change_password_tab, bg=BG)
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
        self.btn_back_change_users_password = Button(self.frame_change_users_password, text='بازگشت به صفحه ورود', cnf=CNF_BTN, command=self.back)
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
        self.btn_back_change_users_password.grid(row=13, column=1, cnf=CNF_GRID)
        self.entry_old_password_change_users_password.bind('<Return>', lambda e: self.entry_password1_change_users_password.focus_set())
        self.entry_password1_change_users_password.bind('<Return>', lambda e: self.entry_password2_change_users_password.focus_set())
        self.entry_password2_change_users_password.bind('<Return>', self.change_users_password)

        if self.connection.user.access_level==1:
            ############################################## frame_user ##############################################
            self.frame_user = Frame(self.frame_add_user_tab, bg=BG)
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
            self.entry_password2.bind('<Return>', self.create_account)

            ############################################# frame_counter #############################################
            self.frame_counter = Frame(self.frame_add_counter_tab, bg=BG)
            self.frame_counter.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            self.label_counter_part = Label(self.frame_counter, text="بخش پارامتر", cnf=CNF_LABEL)
            self.entry_counter_part = ttk.Combobox(self.frame_counter, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')
            self.entry_counter_part.bind("<<ComboboxSelected>>", self.show_places_of_this_part)
            self.label_counter_place = Label(self.frame_counter, text="مکان پارامتر", cnf=CNF_LABEL)
            self.entry_counter_place = ttk.Combobox(self.frame_counter, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')
            self.label_counter_name = Label(self.frame_counter, text="نام پارامتر", cnf=CNF_LABEL)
            self.entry_counter_name = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER, justify='right')
            self.label_counter_type = Label(self.frame_counter, text="نوع پارامتر", cnf=CNF_LABEL)
            self.entry_counter_type = ttk.Combobox(self.frame_counter, values=PARAMETER_TYPES, font=FONT, width=WORDS_WIDTH, justify='center')
            self.entry_counter_type.insert(0, PARAMETER_TYPES[0])
            self.entry_counter_type.config(state='readonly')
            self.entry_counter_type.bind("<<ComboboxSelected>>", self.check_counter_type)
            self.label_counter_unit = Label(self.frame_counter, text="واحد اندازه گیری", cnf=CNF_LABEL)
            self.entry_counter_unit = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            self.label_counter_default_value = Label(self.frame_counter, text="مقدار پیش فرض", cnf=CNF_LABEL)
            self.entry_counter_default_value = ttk.Combobox(self.frame_counter, values=DEFAULT_VALUES, font=FONT, width=WORDS_WIDTH, justify='center')
            self.entry_counter_default_value.insert(0, DEFAULT_VALUES[0])
            self.entry_counter_default_value.config(state='readonly')
            self.label_counter_variable_name = Label(self.frame_counter, text="نام متغیر", cnf=CNF_LABEL)
            self.entry_counter_variable_name = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            self.label_counter_warning_lower_bound = Label(self.frame_counter, text="حد پایین هشدار", cnf=CNF_LABEL)
            self.entry_counter_warning_lower_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            self.label_counter_warning_upper_bound = Label(self.frame_counter, text="حد بالای هشدار", cnf=CNF_LABEL)
            self.entry_counter_warning_upper_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            self.label_counter_alarm_lower_bound = Label(self.frame_counter, text="حد پایین آلارم", cnf=CNF_LABEL)
            self.entry_counter_alarm_lower_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            self.label_counter_alarm_upper_bound = Label(self.frame_counter, text="حد بالای آلارم", cnf=CNF_LABEL)
            self.entry_counter_alarm_upper_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            self.label_counter_formula = Label(self.frame_counter, text="فرمول", cnf=CNF_LABEL)
            self.entry_counter_formula = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            self.label_counter_formula_parameters = Label(self.frame_counter, text="متغیرهای فرمول", cnf=CNF_LABEL)
            self.entry_counter_formula_parameters = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
            self.btn_counter_register = Button(self.frame_counter, text='ایجاد پارامتر', cnf=CNF_BTN, command=self.create_parameter)
            self.btn_counter_update = Button(self.frame_counter, text='ویرایش پارامتر', cnf=CNF_BTN, command=self.update_parameter)
            self.btn_counter_back = Button(self.frame_counter, text='بازگشت به صفحه ورود', cnf=CNF_BTN, command=self.back)
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
            self.entry_counter_formula.grid(row=15, column=5, cnf=CNF_GRID)
            self.label_counter_formula_parameters.grid(row=15, column=3, cnf=CNF_GRID)
            self.entry_counter_formula_parameters.grid(row=15, column=1, cnf=CNF_GRID)
            self.btn_counter_register.grid(row=17, column=7, cnf=CNF_GRID)
            self.btn_counter_update.grid(row=17, column=5, cnf=CNF_GRID)
            self.btn_counter_back.grid(row=17, column=3, cnf=CNF_GRID)
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
            self.entry_counter_formula.bind('<Return>', lambda e: self.entry_counter_formula_parameters.focus_set())
            self.entry_counter_formula_parameters.bind('<Return>', self.create_parameter)

            ############################################# frame_part #############################################
            self.frame_part = Frame(self.frame_add_part_tab, bg=BG)
            self.frame_part.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            # self.frame_part.place(relx=0.22, rely=0.08, relwidth=1, relheight=1)
            self.label_part_name = Label(self.frame_part, text="نام بخش", cnf=CNF_LABEL)
            self.entry_part_name = Entry(self.frame_part, cnf=CNF_ENTRY_COUNTER, justify='right')
            self.entry_part_name.bind("<Return>", self.create_part)
            self.btn_part_register = Button(self.frame_part, text='ایجاد بخش', cnf=CNF_BTN, command=self.create_part)
            self.btn_part_back = Button(self.frame_part, text='بازگشت به صفحه ورود', cnf=CNF_BTN, command=self.back)
            self.label_part_name.grid(row=1, column=7, cnf=CNF_GRID)
            self.entry_part_name.grid(row=1, column=5, cnf=CNF_GRID)
            self.btn_part_register.grid(row=17, column=7, cnf=CNF_GRID)
            self.btn_part_back.grid(row=17, column=5, cnf=CNF_GRID)
            self.treev_part = ttk.Treeview(self.frame_part, height=6, selectmode ='browse', show='headings')
            self.treev_part.grid(row=19, rowspan=3, column=1, columnspan=10, sticky='news')
            self.verscrlbar_part = ttk.Scrollbar(self.frame_part, orient ="vertical", command = self.treev_part.yview)
            self.verscrlbar_part.grid(row=19, rowspan=3, column=11, sticky='ns')
            self.treev_part.configure(yscrollcommand = self.verscrlbar_part.set)
            self.treev_part["columns"] = ("1", "2")
            self.treev_part.column("1", width = 200, anchor ='c')
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
            self.frame_place = Frame(self.frame_add_place_tab, bg=BG)
            self.frame_place.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            # self.frame_place.place(relx=0.2, rely=0.02, relwidth=1, relheight=1)
            self.label_place_part_name = Label(self.frame_place, text="نام بخش", cnf=CNF_LABEL)
            self.entry_place_part_name = ttk.Combobox(self.frame_place, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')
            self.entry_place_part_name.bind("<<ComboboxSelected>>", self.refresh_places_frame_after_selecting_part)
            self.label_place_name = Label(self.frame_place, text="نام مکان", cnf=CNF_LABEL)
            self.entry_place_name = Entry(self.frame_place, cnf=CNF_ENTRY_COUNTER, justify='right', state='readonly')
            self.entry_place_name.bind("<Return>", self.create_place)
            self.btn_place_register = Button(self.frame_place, text='ایجاد مکان جدید', cnf=CNF_BTN, command=self.create_place)
            self.btn_place_back = Button(self.frame_place, text='بازگشت به صفحه ورود', cnf=CNF_BTN, command=self.back)
            self.label_place_part_name.grid(row=1, column=7, cnf=CNF_GRID)
            self.entry_place_part_name.grid(row=1, column=5, cnf=CNF_GRID)
            self.label_place_name.grid(row=3, column=7, cnf=CNF_GRID)
            self.entry_place_name.grid(row=3, column=5, cnf=CNF_GRID)
            self.btn_place_register.grid(row=17, column=7, cnf=CNF_GRID)
            self.btn_place_back.grid(row=17, column=5, cnf=CNF_GRID)
            self.treev_place = ttk.Treeview(self.frame_place, height=6, selectmode ='browse', show='headings')
            self.treev_place.grid(row=19, rowspan=3, column=1, columnspan=10, sticky='news')
            self.verscrlbar_place = ttk.Scrollbar(self.frame_place, orient ="vertical", command = self.treev_place.yview)
            self.verscrlbar_place.grid(row=19, rowspan=3, column=11, sticky='ns')
            self.treev_place.configure(yscrollcommand = self.verscrlbar_place.set)
            self.treev_place["columns"] = ("1", "2")
            self.treev_place.column("1", width = 200, anchor ='c')
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
            self.frame_all_counters = Frame(self.frame_all_counters_tab, bg=BG)
            self.frame_all_counters.pack(side=RIGHT, anchor='ne', padx=PADX, pady=PADY)
            # self.frame_all_counters.place(relx=0.2, rely=0.02, relwidth=1, relheight=1)
            self.btn_all_counters_back = Button(self.frame_all_counters, text='بازگشت به صفحه ورود', cnf=CNF_BTN, command=self.back)
            self.btn_all_counters_back.grid(row=17, column=5, cnf=CNF_GRID)
            self.treev_all_counters = ttk.Treeview(self.frame_all_counters, height=8, selectmode ='browse', show='headings')
            self.treev_all_counters.grid(row=19, rowspan=3, column=1, columnspan=10, sticky='news')
            self.treev_all_counters.bind("<Double-1>", self.change_counter_info)
            self.verscrlbar_all_counters = ttk.Scrollbar(self.frame_all_counters, orient ="vertical", command = self.treev_all_counters.yview)
            self.verscrlbar_all_counters.grid(row=19, rowspan=3, column=11, sticky='ns')
            self.treev_all_counters.configure(yscrollcommand = self.verscrlbar_all_counters.set)
            self.treev_all_counters["columns"] = ("1", "2", "3", "4")
            self.treev_all_counters.column("1", width = 250, anchor ='c')
            self.treev_all_counters.column("2", width = 200, anchor ='c')
            self.treev_all_counters.column("3", width = 200, anchor ='c')
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
    def check_counter_type(self, event=None):
        counter_type = self.entry_counter_type.get()
        self.entry_counter_default_value.config(state='normal')
        self.entry_counter_default_value.delete(0, END)
        if counter_type in PARAMETER_TYPES[0:2]: # یعنی یا کنتور معمولی باشه یا ثابت
            self.entry_counter_default_value.insert(0, DEFAULT_VALUES[0])
            self.entry_counter_default_value.config(values=DEFAULT_VALUES)
        elif counter_type==PARAMETER_TYPES[2]: # یعنی از نوع محاسباتی باشه
            self.entry_counter_default_value.config(values=[])
        self.entry_counter_default_value.config(state='readonly')
        if counter_type==PARAMETER_TYPES[1]: # fixed:
            self.entry_counter_formula.delete(0, END)
            self.entry_counter_formula.config(state='readonly')
            self.entry_counter_formula_parameters.delete(0, END)
            self.entry_counter_formula_parameters.config(state='readonly')
        else:
            self.entry_counter_formula.config(state='normal')
            self.entry_counter_formula_parameters.config(state='normal')

    # تابعی جهت ایجاد پارامتر
    def create_parameter(self, event=None):
        global all_variables_current_value_and_workout
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
        formula_parameters = self.entry_counter_formula_parameters.get().strip()
        if part == "":
            msb.showwarning("هشدار", "پارامتر مربوط به کدام بخش است؟")
            self.entry_counter_part.focus_set()
            return
        if place == "":
            msb.showwarning("هشدار", "پارامتر مربوط به کدام مکان است؟")
            self.entry_counter_place.focus_set()
            return
        if name == "":
            msb.showwarning("هشدار", "نام پارامتر را وارد کنید")
            self.entry_counter_name.focus_set()
            return
        if unit == "":
            unit=None
        parameters_variable_names = self.connection.get_all_parameters_variable_names()
        problem = what_is_variable_name_problem(variable_name, parameters_variable_names)
        if problem:
            msb.showwarning("هشدار", problem)
            self.entry_counter_variable_name.focus_set()
            return
        if warning_lower_bound == "":
            warning_lower_bound=0
        else:
            try:
                warning_lower_bound = float(warning_lower_bound)
            except:
                msb.showwarning("هشدار", "لطفا حد پایین هشدار را به صورت عددی وارد کنید")
                self.entry_counter_warning_lower_bound.focus_set()
                return
        if warning_upper_bound == "":
            warning_upper_bound=9999999999
        else:
            try:
                warning_upper_bound = float(warning_upper_bound)
            except:
                msb.showwarning("هشدار", "لطفا حد بالای هشدار را به صورت عددی وارد کنید")
                self.entry_counter_warning_upper_bound.focus_set()
                return
        if alarm_lower_bound == "":
            alarm_lower_bound=0
        else:
            try:
                alarm_lower_bound = float(alarm_lower_bound)
            except:
                msb.showwarning("هشدار", "لطفا حد پایین آلارم را به صورت عددی وارد کنید")
                self.entry_counter_alarm_lower_bound.focus_set()
                return
        if alarm_upper_bound == "":
            alarm_upper_bound=9999999999
        else:
            try:
                alarm_upper_bound = float(alarm_upper_bound)
            except:
                msb.showwarning("هشدار", "لطفا حد بالای آلارم را به صورت عددی وارد کنید")
                self.entry_counter_alarm_upper_bound.focus_set()
                return
        if formula != "":
            result = what_is_formula_problem(formula, formula_parameters, variable_name, parameters_variable_names)
            if isinstance(result, str): # یعنی اگه یه استرینگ داده بود، مشکلی هست. پس ارور رو نشون بده.
                msb.showwarning("هشدار", result)
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
                    result = what_is_formula_problem(formula, ' '.join(result), variable_name, parameters_variable_names)
                    if isinstance(result, list):
                        is_everything_ok=True
                    else:
                        is_everything_ok=False
                        msb.showwarning('هشدار', result)
        if formula == "" and type in [PARAMETER_TYPES[0], PARAMETER_TYPES[2]]:
            msb.showwarning("هشدار", "برای پارامترهای محاسباتی و کنتور، فرمول نمیتواند خالی باشد")
            self.entry_counter_formula.focus_set()
            return
        if is_everything_ok:
            result_message, _ = self.connection.create_parameter(name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place)
        else:
            return
        if result_message=='ok':
            # اگه ساخته شده باشه، تو دیتابیس تغییر کرده اما برنامه ازش خبر نداریم. پس دیکشنری مربوط به اون رو هم آپدیت میکنیم.
            # چون تازه ساخته شده هر دو مقدار رو صفر میذاریم و اگه بعدا ثبت کنیم خود به خود لاگ براش ثبت میشه.
            # فقط ایجا داخل سلف ذخیره اش نکرده بودم چون موقت بود و اسم متغیرش همون وریبل نیم هست بدون سل.
            all_variables_current_value_and_workout.update({
                variable_name: {
                    'value': 0,
                    'workout': 0
                }
            })
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
        formula_parameters = self.entry_counter_formula_parameters.get().strip()
        if part == "":
            msb.showwarning("هشدار", "پارامتر مربوط به کدام بخش است؟")
            self.entry_counter_part.focus_set()
            return
        if place == "":
            msb.showwarning("هشدار", "پارامتر مربوط به کدام مکان است؟")
            self.entry_counter_place.focus_set()
            return
        if name == "":
            msb.showwarning("هشدار", "نام پارامتر را وارد کنید")
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
                msb.showwarning("هشدار", "لطفا حد پایین هشدار را به صورت عددی وارد کنید")
                self.entry_counter_warning_lower_bound.focus_set()
                return
        if warning_upper_bound == "":
            warning_upper_bound=None
        else:
            try:
                warning_upper_bound = float(warning_upper_bound)
            except:
                msb.showwarning("هشدار", "لطفا حد بالای هشدار را به صورت عددی وارد کنید")
                self.entry_counter_warning_upper_bound.focus_set()
                return
        if alarm_lower_bound == "":
            alarm_lower_bound=None
        else:
            try:
                alarm_lower_bound = float(alarm_lower_bound)
            except:
                msb.showwarning("هشدار", "لطفا حد پایین آلارم را به صورت عددی وارد کنید")
                self.entry_counter_alarm_lower_bound.focus_set()
                return
        if alarm_upper_bound == "":
            alarm_upper_bound=None
        else:
            try:
                alarm_upper_bound = float(alarm_upper_bound)
            except:
                msb.showwarning("هشدار", "لطفا حد بالای آلارم را به صورت عددی وارد کنید")
                self.entry_counter_alarm_upper_bound.focus_set()
                return
        if formula != "":
            parameters_variable_names = self.connection.get_all_parameters_variable_names()
            result = what_is_formula_problem(formula, formula_parameters, variable_name, parameters_variable_names)
            if isinstance(result, str): # یعنی اگه یه استرینگ داده بود، مشکلی هست. پس ارور رو نشون بده.
                msb.showwarning("هشدار", result)
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
                    result = what_is_formula_problem(formula, ' '.join(result), variable_name, parameters_variable_names)
                    if isinstance(result, list):
                        is_everything_ok=True
                    else:
                        is_everything_ok=False
                        msb.showwarning('هشدار', result)
        if formula == "" and type in [PARAMETER_TYPES[0], PARAMETER_TYPES[2]]:
            msb.showwarning("هشدار", "برای پارامترهای محاسباتی و کنتور، فرمول نمیتواند خالی باشد")
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
        self.entry_counter_default_value.config(state='normal')
        self.entry_counter_formula.config(state='normal')
        self.entry_counter_formula_parameters.config(state='normal')
        self.entry_counter_part.delete(0, END)
        self.entry_counter_place.delete(0, END)
        self.entry_counter_name.delete(0, END)
        self.entry_counter_type.delete(0, END)
        self.entry_counter_unit.delete(0, END)
        self.entry_counter_default_value.delete(0, END)
        self.entry_counter_variable_name.delete(0, END)
        self.entry_counter_warning_lower_bound.delete(0, END)
        self.entry_counter_warning_upper_bound.delete(0, END)
        self.entry_counter_alarm_lower_bound.delete(0, END)
        self.entry_counter_alarm_upper_bound.delete(0, END)
        self.entry_counter_formula.delete(0, END)
        self.entry_counter_formula_parameters.delete(0, END)
        self.entry_counter_part.insert(0, temp_part)
        self.entry_counter_place.insert(0, temp_place)
        self.entry_counter_name.insert(0, temp_name)
        self.entry_counter_type.insert(0, temp_counter.type)
        self.entry_counter_default_value.insert(0, temp_counter.default_value)
        self.entry_counter_variable_name.insert(0, temp_counter.variable_name)
        self.entry_counter_formula.insert(0, temp_counter.formula)
        if temp_counter.unit:
            self.entry_counter_unit.insert(0, temp_counter.unit)
        if temp_counter.warning_lower_bound:
            self.entry_counter_warning_lower_bound.insert(0, round3(temp_counter.warning_lower_bound))
        if temp_counter.warning_upper_bound:
            self.entry_counter_warning_upper_bound.insert(0, round3(temp_counter.warning_upper_bound))
        if temp_counter.alarm_lower_bound:
            self.entry_counter_alarm_lower_bound.insert(0, round3(temp_counter.alarm_lower_bound))
        if temp_counter.alarm_upper_bound:
            self.entry_counter_alarm_upper_bound.insert(0, round3(temp_counter.alarm_upper_bound))
        self.entry_counter_part.config(state='readonly')
        self.entry_counter_place.config(state='readonly')
        self.entry_counter_type.config(state='readonly')
        self.entry_counter_default_value.config(state='readonly')
        self.check_counter_type()

    ########################################## create part functions ###########################################
    # تابعی جهت ساخت بخش
    def create_part(self, event=None):
        title = self.entry_part_name.get().strip()
        if title=="":
            msb.showwarning("هشدار", "نام بخش نمیتواند خالی باشد.")
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
            msb.showerror("هشدار", f"ابتدا باید ترتیب بخش ها را مشخص کنید و سپس روی دکمه تایید بزنید.")

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
            msb.showwarning("هشدار", "نام مکان یا بخش نمیتواند خالی باشد.")
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
            msb.showerror("هشدار", f"ابتدا باید یک بخش را انتخاب کنید و مکان های آن را مرتب کنید. سپس روی دکمه تایید بزنید.")


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
        all_counter_widgets= [] # یه لیست از تمام کنتور ویجت هایی که میسازیم رو ذخیره میکنم که وسط برنامه بشه تغییرشون داد. هر بار که تابع سید تبز او پارتز صدا میشه، این لیست خالی میشه. چون از اول اومده. داخل رفرشی که میخوام بنویسم فقط تغییر میکنن. پاک نمیشن. اما اگه بخش یا مکان جدیدی به دیتابیس اضافه بشه، همه چیز از اول شروع میشه و این لیست هم از نو تعریف میشه.
        for item in self.tab_control_frame.winfo_children():
            item.destroy()
        all_parts=self.connection.get_all_parts() # یک لیست تک بعدی از کل بخش ها
        all_parts.reverse() # خودش گفته بود که ترتیب از راست به چپ بشه به خاطر همین ریورس کردم اینجا. دقت کنم که جاش همین جاست. اگه بعدا ریورس کنم، اطلاعات رو اشتباه مینویسه.
        # print(all_parts)
        # for p in all_parts:
        #     print(p)
        all_places = [] # یک لیست دو بعدی از کل مکان ها. تو لایه اول بخش ها هستند و لایه دوم، مکان های اون بخش.
        for part in all_parts:
            temp_places=self.connection.get_all_places_by_part_id(part.id)
            all_places.append(temp_places)
        # print(all_places)
        # for places in all_places:
        #     print(places)
        self.all_counters_2d = [] # لیست دو بعدی از تمام کنتور ها برای ارسال به پارت ویجت که تمام کنتورهای یک بخش رو بسازه. دو بعدی هست. دقت کنم که بعضی از لیست هاش هم خالی هستند. چون بخشی هست که ممکنه کنتوری نداشته باشه.
        for places in all_places: # آل پلیسس یه لیست از مکان های هر بخش هست. پس روش دوباره حلقه میزنیم
            for place in places:
                self.all_counters_2d.append(self.connection.get_all_parameters_of_this_part_and_place(part_id=place.part_id, place_id=place.id))
        # print(self.all_counters_2d)
        # for counters in self.all_counters_2d:
        #     print(counters)
        self.set_logged_parts_names()
        tabs_list = []
        parts_tab = []
        for i, part in enumerate(all_parts):
            tabs_list.append(Frame(self.tab_control_frame))
            tabs_list[i].pack()
            self.tab_control_frame.add(tabs_list[i], text =f'{part.title}')
            places_with_counters = []
            for place in all_places[i]:
                counters = self.connection.get_all_parameters_of_this_part_and_place(part_id=place.part_id, place_id=place.id)
                places_with_counters.append(counters)
            parts_tab.append(PartWidget(self.connection, tabs_list[i], places_with_counters))
            parts_tab[i].pack()
        self.tab_control_frame.pack(expand=1, fill="both")
        for i, counter_widget in enumerate(all_counter_widgets):
            counter_widget: CounterWidget
            if counter_widget.type==PARAMETER_TYPES[2]:
                pass # چون اصلا نمیشه روش اینتر زد.
            else:
                counter_widget.entry_workout.bind('<Return>', lambda e, i=i: self.goto_next_counter_widget(i)) # چون هر دو نوع ثابت و کنتور، این ویجت رو دارند و انتری هست.
                if counter_widget.type==PARAMETER_TYPES[0]: # نوع کنتور، یه انتری دیگه هم داره. پس اون رو هم بایند میکنیم.
                    counter_widget.entry_current_counter.bind('<Return>', lambda e, i=i: self.goto_next_counter_widget(i))

    def goto_next_counter_widget(self, index):
        global all_counter_widgets
        length = len(all_counter_widgets)
        for i in range(index+1, length):
            if all_counter_widgets[i].type==PARAMETER_TYPES[2]:
                continue
            elif all_counter_widgets[i].type==PARAMETER_TYPES[1]:
                all_counter_widgets[i].entry_workout.focus_set()
                return
            elif all_counter_widgets[i].type==PARAMETER_TYPES[0]:
                if all_counter_widgets[i].boolean_var_bad.get():
                    all_counter_widgets[i].entry_workout.focus_set()
                else:
                    all_counter_widgets[i].entry_current_counter.focus_set()
                return

    def disable_confirm_button(self, event=None):
        self.btn_confirm_counter_log_insert.config(state='disabled')
        self.btn_confirm_counter_log_update.config(state='disabled')
        
    def enable_or_disable_confirm_button(self, event=None):
        global all_counter_widgets
        # با این که تابع جدا برای دیسیبل کردن نوشتم. ولی حالات زیادی برای باگ خوردن داشت.
        # باز هم گفتم برای باگ نخوردن، اینجا هم یه بار دیسیبل کنم و بعد با شرط اونی که اوکی هست
        # رو اینیبل کنم.
        self.btn_confirm_counter_log_insert.config(state='disabled')
        self.btn_confirm_counter_log_update.config(state='disabled')
        part_name = self.tab_control_frame.tab(self.tab_control_frame.select(), "text")
        if part_name in self.logged_parts_names:
            self.btn_confirm_counter_log_update.config(state='normal')
            for counter_widget in all_counter_widgets:
                counter_widget: CounterWidget
                if counter_widget.type in PARAMETER_TYPES[1:3]:
                    continue
                elif counter_widget.type==PARAMETER_TYPES[0]:
                    previous_value = counter_widget.connection.get_previous_value_of_parameter_by_id_and_date(counter_widget.id, date_picker.get_date())
                    counter_widget.label_previous_counter.config(text=round3(previous_value))
                    counter_widget.entry_workout.config(state='normal')
                    counter_widget.entry_workout.delete(0, END)
                    if counter_widget.counter_log and counter_widget.counter_log.is_ok==0: # قبل از اند اون رو گذاشتم چون اگه رکوردی نبود نان میداد و خب نمیشه از تو هیچی ایز اوکی رو در آورد.
                        counter_widget.boolean_var_bad.set(1)
                        counter_widget.check()
                        counter_widget.entry_workout.insert(0, round3(counter_widget.counter_log.workout))
                    else:
                        counter_widget.entry_workout.insert(0, round3(counter_widget.answer))
                    counter_widget.entry_workout.config(state='disabled')
                    counter_widget.update_workout()
        else:
            self.btn_confirm_counter_log_insert.config(state='normal')

    def set_logged_parts_names(self):
        global date_picker
        self.logged_parts_names.clear()
        temp_date = date_picker.get_date()
        for counters in self.all_counters_2d:
            for counter in counters:
                counter: Counter
                last_log = self.connection.get_last_log_of_parameter_by_id(counter.id)
                if last_log!=None and temp_date<=last_log:
                    self.logged_parts_names.add(counter.part_title)

    def confirm_log_insert(self, event=None):
        temp_date = date_picker.get_date()
        if temp_date == None:
            msb.showerror("هشدار", "لطفا تاریخ را به درستی انتخاب کنید")
            return
        part_name = self.tab_control_frame.tab(self.tab_control_frame.select(), "text")
        result = self.precheck_before_confirm(part_name)
        if result==None:
            return
        message = "لطفا یک بار دیگر به دقت اطلاعات را بررسی نمایید\n"
        message += "با انتخاب دکمه تایید، تمامی اطلاعات این بخش در دیتابیس ذخیره میشوند\n"
        message += "در صورت اطمنیان، دکمه تایید را فشار دهید"
        self.root.bell()
        answer = msb.askyesno("هشدار", message)
        if not answer:
            return
        print(temp_date)
        for counter_widget in all_counter_widgets:
            counter_widget: CounterWidget
            if counter_widget.part_title==part_name:
                if counter_widget.type in PARAMETER_TYPES[1:3]:
                    result_message, ـ = counter_widget.connection.create_parameter_log(counter_widget.workout, counter_widget.workout, 1, temp_date, counter_widget.id, self.user.id)
                elif counter_widget.type==PARAMETER_TYPES[0]:
                    is_ok = 1 if counter_widget.boolean_var_bad.get()==False else 0
                    result_message, ـ = counter_widget.connection.create_parameter_log(counter_widget.b, counter_widget.workout, is_ok, temp_date, counter_widget.id, self.user.id)
        if result_message == "ok":
            self.btn_confirm_counter_log_insert.config(state='disabled')
            self.btn_confirm_counter_log_update.config(state='normal')
            message = f"اطلاعات بخش {part_name} با موفقیت در دیتابیس اضافه شدند"
            msb.showinfo('success', message)
        else:
            msb.showerror("ارور", result_message)

    # تابی برای بررسی این که اعداد با ظاهر فعلی در صفحه در دیتابیس ذخیره شوند یا نه
    # اگر اشتباه باشند که اجازه نمیدهد. اگر منفی باشند کاربر باید تایید کند تا به مرحله بعد برود.
    def precheck_before_confirm(self, part_name):
        negative_numbers = 0
        for counter_widget in all_counter_widgets:
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
        temp_date = date_picker.get_date()
        if temp_date == None:
            msb.showerror("هشدار", "لطفا تاریخ را به درستی انتخاب کنید")
            return
        part_name = self.tab_control_frame.tab(self.tab_control_frame.select(), "text")
        result = self.precheck_before_confirm(part_name)
        if result==None:
            return
        message = "لطفا یک بار دیگر به دقت اطلاعات را بررسی نمایید\n"
        message += "با انتخاب دکمه تایید، تمامی اطلاعات این بخش در دیتابیس ویرایش میشوند\n"
        message += "در صورت اطمنیان، دکمه تایید را فشار دهید"
        self.root.bell()
        answer = msb.askyesno("هشدار", message)
        if not answer:
            return
        for counter_widget in all_counter_widgets:
            counter_widget: CounterWidget
            if counter_widget.part_title==part_name:
                if counter_widget.type in PARAMETER_TYPES[1:3]:
                    result_message, ـ = counter_widget.connection.update_parameter_log(counter_widget.workout, counter_widget.workout, 1, temp_date, counter_widget.id, self.user.id)
                elif counter_widget.type==PARAMETER_TYPES[0]:
                    is_ok = 1 if counter_widget.boolean_var_bad.get()==False else 0
                    result_message, ـ = counter_widget.connection.update_parameter_log(counter_widget.b, counter_widget.workout, is_ok, temp_date, counter_widget.id, self.user.id)
        if result_message == "ok":
            message = f"اطلاعات بخش {part_name} با موفقیت در دیتابیس ویرایش شدند"
            msb.showinfo('success', message)
            self.update_next_logs_because_they_may_be_related_to_this_logs()
        else:
            msb.showerror("ارور", result_message)

    def update_next_logs_because_they_may_be_related_to_this_logs(self):
        global all_variables_current_value_and_workout, all_counter_widgets
        temp_date = date_picker.get_date()
        # برای اینکه ایزوله باشه و کار بقیه برنامه رو خراب نکنه، تو یه متغیر جدید ذخیره کردم و همینجا
        # فقط ازش استفاده میشه. این تابع که تموم شه دیگه کاری باهاش نداریم
        updated_logs = self.connection.get_parameters_log_by_date(temp_date)
        next_day_logs = self.connection.get_parameters_next_log_by_date(temp_date)
        for counters in self.all_counters_2d:
            for counter in counters:
                counter: Counter
                if counter.formula != "":
                    parameters = get_formula_parameters(counter.formula)
                    values = []
                    for p in parameters:
                        if p=='b':
                            values.append(next_day_logs.get(counter.variable_name).value)
                        elif p=='a':
                            values.append(updated_logs.get(counter.variable_name).value)
                        else:
                            values.append(updated_logs.get(p).workout)
                    answer = calculate_fn(counter.formula, parameters, values)
                if counter.type==PARAMETER_TYPES[2]:
                    next_day_logs[counter.variable_name].workout=answer
                elif counter.type==PARAMETER_TYPES[1]:
                    pass # پارامترهای ثابت، وابسته به بقیه نیستند. پس تغییری نمیکنند.
                elif counter.type==PARAMETER_TYPES[0]:
                    # پارامترهای کنتور، اگه سالم باشن باید تغییر کنند. اما اگه خراب باشن، به مقدار ورک اوتشون دست نمیزنیم و همون قبلی میمونن
                    if next_day_logs[counter.variable_name].is_ok:
                        next_day_logs[counter.variable_name].workout=answer
                    else:
                        pass
        for log in next_day_logs.values():
            self.connection.change_log_by_computer_id(log)
        del updated_logs
        del next_day_logs


    ########################################### generic functions ###########################################
    # تابعی جهت برگشتن به صفحه احراز هویت از برنامه
    def back(self, event=None):
        self.is_staff_window_running=False
        self.main_window.destroy()
        self.root.deiconify()

    def refresh_ui(self):
        if self.connection.user.access_level==1:
            self.refresh_parts_tree_view()
            self.refresh_parts_values_in_comboboxes()
            # self.refresh_places_tree_view() # این ورودی میخواد. به خاطر همین کامنت کردم. گذاشتم که بعدا اشتباهی دوباره نذارمش.
            self.refresh_places_frame_after_selecting_part()
            self.refresh_all_counters_treeview()
        self.seed_tabs_of_parts()
        self.enable_or_disable_confirm_button()


    def refresh_ui_from_anywhere(self):
        global signal
        sleep(0.4)
        while self.is_staff_window_running:
            sleep(0.01)
            if signal:
                signal=0
                self.refresh_ui()
                self.tab_control.select(self.frame_add_statistics_tab)
    
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
    years_list = [i for i in range(1400, 1410)]
    def __init__(self, connection: Connection, root: Tk):
        super().__init__(connection, root)
        self.year = StringVar(self.frame)
        self.month = StringVar(self.frame)
        self.day = StringVar(self.frame)
        self.btn_yesterday = Button(self.frame, text='روز قبل', cnf=CNF_BTN, font=FONT3, padx=0, pady=0, command=lambda: self.time_delta(-1))
        self.btn_tomorrow = Button(self.frame, text='روز بعد', cnf=CNF_BTN, font=FONT3, padx=0, pady=0, command=lambda: self.time_delta(1))
        self.combo_year = ttk.Combobox(self.frame, values=self.years_list, textvariable=self.year, width=7, state='readonly', font=FONT, justify='center')
        self.combo_month = ttk.Combobox(self.frame, values=self.months_list, textvariable=self.month, width=5, state='readonly', font=FONT, justify='center')
        self.combo_day = ttk.Combobox(self.frame, values=self.days_list, textvariable=self.day, width=5, state='readonly', font=FONT, justify='center')
        self.combo_year.bind("<<ComboboxSelected>>", self.check_date)
        self.combo_month.bind("<<ComboboxSelected>>", self.check_date)
        self.combo_day.bind("<<ComboboxSelected>>", self.check_date)
        self.label_date = Label(self.frame, text="!!! تاریخ نامعتبر !!!", cnf=CNF_LABEL, pady=32, width=20)
        self.btn_yesterday.pack(cnf=CNF_PACK2)
        self.combo_day.pack(cnf=CNF_PACK2)
        self.combo_month.pack(cnf=CNF_PACK2)
        self.combo_year.pack(cnf=CNF_PACK2)
        self.btn_tomorrow.pack(cnf=CNF_PACK2)
        self.label_date.pack(cnf=CNF_PACK2)
        self.refresh_date()

    def refresh_date(self, date=None):
        global selected_date, all_variables_current_value_and_workout
        if date==None: # این برای اول کار هست. وقتی که تابع تایم دلتا این رو صدا میکنه بهش روز رو میده و نان نیست. پس این ایف اجرا نمیشه.
            date=get_jnow()
            if self.connection.user.default_date==DEFAULT_DATE_VALUES[0]:
                d = jdatetime.timedelta(days=-1)
            elif self.connection.user.default_date==DEFAULT_DATE_VALUES[2]:
                d = jdatetime.timedelta(days=1)
            else:
                d = jdatetime.timedelta(days=0)
            date = date+d
        selected_date = date.togregorian()
        all_variables_current_value_and_workout=self.connection.get_all_parameters_current_value_and_workout(selected_date) # این رو آخر سر اضافه کردم. برای این که مدام از دیتابیس نپرسیم مقادیر رو، اول کار مقدار فعلی همه متغیرها رو میگیریم که تو برنامه راحت بشه باهاشون کار کرد هی نریم سراغ دیتابیس. هر بار هم که تابع رفرش یو آی صدا زده میشه این متغیر رو با همین دستور آپدیت میکنم منتهی چون تو کلاس دیگه هم لازم داشتم، به جای ذخیره کردن در سلف، گلوبالش کردم.
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
        y = self.year.get()
        m = self.month.get()
        d = self.day.get()
        try:
            date = jdatetime.date(int(y), int(m), int(d))
            temp = f"{'تاریخ':10} {WEEKDAYS.get(date.weekday())} {d} {MONTH_NAMES.get(int(m))} {y}"
            self.label_date.config(text=temp)
            self.confirm()
        except ValueError:
            temp = "!!! تاریخ نامعتبر !!!"
            self.label_date.config(text=temp)

    def confirm(self):
        global selected_date, all_variables_current_value_and_workout, signal
        now = datetime.now()
        jdate = jdatetime.datetime(int(self.combo_year.get()), int(self.combo_month.get()), int(self.combo_day.get()), now.hour, now.minute, now.second)
        selected_date = jdate.togregorian()
        all_variables_current_value_and_workout=self.connection.get_all_parameters_current_value_and_workout(selected_date)
        signal=1

    def time_delta(self, days):
        try:
            now = datetime.now()
            jdate = jdatetime.datetime(int(self.combo_year.get()), int(self.combo_month.get()), int(self.combo_day.get()), now.hour, now.minute, now.second)
            d = jdatetime.timedelta(days=days)
            new_date = jdate + d
            self.refresh_date(new_date)
        except ValueError:
            msb.showerror('', "تاریخ به درستی انتخاب نشده است")

    def get_date(self):
        try:
            jdate = jdatetime.date(int(self.combo_year.get()), int(self.combo_month.get()), int(self.combo_day.get()))
            date = jdate.togregorian()
            return date
        except:
            return None
        

class PartWidget(MyWindows):
    def __init__(self, connection: Connection, root: Tk, places_with_counters):
        super().__init__(connection, root)
        global all_counter_widgets
        self.places_with_counters=places_with_counters # یک لیستی از مکان ها با پارامترهایی که داخلشون هست. یعنی یک لیستی از تاپل ها که هر کودوم از تاپل ها هر عضوشون یه پارامتر هست.
        self.my_canvas = Canvas(self.frame, width=S_WIDTH*1.02, height=S_HEIGHT*0.8, bg=BG)
        self.ver_scrollbar = Scrollbar(self.frame, orient=VERTICAL, command=self.my_canvas.yview)
        self.hor_scrollbar = Scrollbar(self.frame, orient=HORIZONTAL, command=self.my_canvas.xview)
        self.my_canvas.configure(yscrollcommand=self.ver_scrollbar.set, xscrollcommand=self.hor_scrollbar.set)
        self.my_canvas.grid(row=1, column=1, sticky='news')
        # self.bg_pic = Image.open('bg_pic.png')
        # self.bg_pic.putalpha(127)
        # self.bg_pic = self.bg_pic.resize((S_WIDTH, S_HEIGHT))
        # self.bg_pic = ImageTk.PhotoImage(self.bg_pic)
        # self.label_background = Label(self.my_canvas, image=self.bg_pic)
        # self.label_background.place(x=0, y=0, width=S_WIDTH, height=S_HEIGHT)
        self.ver_scrollbar.grid(row=1, column=3, sticky='ns')
        self.hor_scrollbar.grid(row=2, column=1, columnspan=3, sticky='ew')
        self.my_canvas.bind('<Configure>', lambda e: self.my_canvas.configure(scrollregion=self.my_canvas.bbox("all")))
        self.places_window = Frame(self.my_canvas, bg=BG)
        self.my_canvas.create_window((0, 0), window=self.places_window, anchor="ne")
        for i, counters in enumerate(self.places_with_counters):
            if counters: # یعنی اگر یک مکان پارامتر هایی داشت این کارها رو انجام بده اگه نداشت الکی ردیف براش درست نکنه
                self.frame_row = Frame(self.places_window, bg=BG)
                for index in range(994, 1000):
                    self.frame_row.columnconfigure(index=index, weight=1, minsize=190)
                self.frame_row.columnconfigure(index=1000, weight=1, minsize=120)
                self.frame_row.grid(sticky='e')
                place_name=counters[0].place_title
                Label(self.frame_row, text=place_name, font=FONT2, bg=BG, fg=FG, width=WORDS_WIDTH//2).grid(row=i, column=1000, sticky='news', padx=4, pady=2)
                for j, counter in enumerate(counters):
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
                        font=FONT2)
                    all_counter_widgets.append(c)
                    c.grid(row=i, column=1000-1-j, sticky='news', padx=4, pady=2)

class CounterWidget(Counter, MyWindows):
    def __init__(self, connection: Connection, root: Tk, part, place, name, variable_name, formula='', type='کنتور', default_value=0, unit=None, warning_lower_bound=None, warning_upper_bound=None, alarm_lower_bound=None, alarm_upper_bound=None, id=None, place_title=None, part_title=None, *args, **kwargs):
        super().__init__(part, place, name, variable_name, formula, type, default_value, unit, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, id, place_title, part_title)
        MyWindows.__init__(self, connection, root)
        global all_variables_current_value_and_workout, date_picker
        self.counter_log = self.connection.get_parameter_log_by_parameter_id_and_date(self.id , date_picker.get_date()) # اطلاعات آخرین لاگ این تاریخ رو موقع تعریف کنتور ویجت گرفتم که مثلا اگه خراب بود بتونم تیکش رو فعال کنم. اما گفت لازم نیست. دیگه پاک نکردم. داخل سلف ذخیره اش کردم. اگه لازم شد استفاده کنم بعدا دارمش. نشد هم که بهتر 
        self.a = self.b = round3(float(all_variables_current_value_and_workout.get(self.variable_name).get('value')))
        self.frame = LabelFrame(self.root, text=self.name, cnf=CNF_LBL_FRM, padx=PADX, pady=PADY, labelanchor='n', bg=BG, fg=FG, *args, **kwargs)
        # my_tool_tip(self.frame, text=self.counter_log.users_full_name)
        self.answer = '' # چیزی که قراره تو کنتور نوشته بشه، پیشفرضش خالی هست. اگه تغییر ندادیم خالی میمونه. اگه تغییر بدیم که بر اساس نوع پارامتر عوض میشه.
        if self.formula != "":
            parameters = get_formula_parameters(self.formula)
            values = []
            for p in parameters:
                if p in ['a', 'b']:
                    values.append(self.b)
                else:
                    values.append(round3(float(all_variables_current_value_and_workout.get(p).get('workout'))))
            self.answer = calculate_fn(self.formula, parameters, values)
        if self.type==PARAMETER_TYPES[2]:
            self.entry_workout = Label(self.frame, text=self.answer, cnf=CNF_LBL2, width=17, height=2, *args, **kwargs)
        elif self.type==PARAMETER_TYPES[1]:
            self.entry_workout = Entry(self.frame, cnf=CNF_ENTRY2, width=25, *args, **kwargs)
            self.frame.bind('<FocusOut>', self.next)
            self.entry_workout.bind('<KeyRelease>', self.update_workout)
            if self.default_value==DEFAULT_VALUES[0]:
                self.entry_workout.insert(0, round3(self.a))
            elif self.default_value==DEFAULT_VALUES[1]:
                self.entry_workout.insert(0, DEFAULT_VALUES[1])
            elif self.default_value==DEFAULT_VALUES[2]:
                self.entry_workout.delete(0, END)
        elif self.type==PARAMETER_TYPES[0]:
            self.img = Image.open('copy-icon.png')
            self.img = self.img.resize((COPY_ICON_SIZE, COPY_ICON_SIZE))
            self.img = ImageTk.PhotoImage(self.img)
            self.btn_copy = Label(self.frame, image=self.img, cnf=CNF_BTN2, relief='raised', *args, **kwargs)
            self.btn_copy.bind('<Button-1>', self.copy_paste)
            # self.btn_info = Label(self.frame, text='🛈', cnf=CNF_BTN, relief='flat', *args, **kwargs)
            # create_tool_tip(self.btn_info, text=self.counter_log.users_full_name)
            self.entry_current_counter = Entry(self.frame, cnf=CNF_ENTRY2, width=WORDS_WIDTH2+1, *args, **kwargs)
            self.label_previous_counter = Label(self.frame, cnf=CNF_LBL2, text=round3(self.a), *args, **kwargs)
            self.entry_workout = Entry(self.frame, cnf=CNF_ENTRY2, width=WORDS_WIDTH3, *args, **kwargs)
            self.boolean_var_bad = BooleanVar(self.frame)
            # self.boolean_var_bad.set(!self.counter_log.is_ok) # اطلاعات رو از دیتابیس گرفته بودم. اما گفت پیش فرض همه سالم باشن. پس من تغییرش ندادم. کدش رو گذاشتم بمونه که اگه لازم شد دوباره ننویسم.
            self.checkbutton_bad = Checkbutton(self.frame, cnf=CNF_CHB2, variable=self.boolean_var_bad, text='خرابی', command=self.check)
            self.frame.bind('<FocusOut>', self.next)
            self.entry_current_counter.bind('<KeyRelease>', self.update_workout)
            self.entry_workout.bind('<KeyRelease>', self.update_workout)
            if self.default_value==DEFAULT_VALUES[0]:
                self.entry_current_counter.insert(0, round3(self.a))
            elif self.default_value==DEFAULT_VALUES[1]:
                self.entry_current_counter.insert(0, DEFAULT_VALUES[1])
            elif self.default_value==DEFAULT_VALUES[2]:
                self.entry_current_counter.delete(0, END)
            self.entry_workout.insert(0, self.answer)
            self.entry_workout.config(state='readonly')
            self.entry_current_counter.grid(row=2, column=2, cnf=CNF_GRID2)
            self.btn_copy.grid(row=2, column=3, cnf=CNF_GRID2)
            # self.btn_info.grid(row=3, column=3, cnf=CNF_GRID2)
            self.checkbutton_bad.grid(row=3, column=1, cnf=CNF_GRID2)
            self.label_previous_counter.grid(row=3, column=2, columnspan=2, cnf=CNF_GRID2)
        self.entry_workout.grid(row=2, column=1, cnf=CNF_GRID2)
        self.check_color()
        self.next() # پارامترهایی از جنس کنتور که فرمول محاسباتی از بقیه کنتورها داشتن، مقدار قبلی دیتابیس رو مینوشتن و باید روی فیلدهای وابسته به فرمولشون کلیک میکردیم و جابه جا میشدیم تا فوکس اوت کنه و مقدارشون بر اساس داده هایی باشه که در صفحه در حال نمایش هستند. این تابع رو به خاطر همین صدا کردم که خودش این کار رو بکنه. اگه به باگ خوردم بازم ازش کپی پیست کنم. تابع خیلی خوبی هست :D
 
    def check_color(self, event=None):
        w_l = self.warning_lower_bound
        w_u = self.warning_upper_bound
        a_l = self.alarm_lower_bound
        a_u = self.alarm_upper_bound
        bg=ALARM_COLOR # یه سری ارور میداد با این که ترای و اکسپت گذاشته بودم. خلاصه حالتی پیش میومد که میگفت بی جی تعریف شده نیست.
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
                bg = ALARM_COLOR
            elif isinstance(w_l, Decimal) and self.workout<w_l:
                bg = WARNING_COLOR
            elif isinstance(a_u, Decimal) and self.workout>a_u:
                bg = ALARM_COLOR
            elif isinstance(w_u, Decimal) and self.workout>w_u:
                bg = WARNING_COLOR
            else:
                bg=BG
        except ValueError:
            bg=ALARM_COLOR
        except TypeError:
            bg=ALARM_COLOR
        finally:
            if self.type==PARAMETER_TYPES[0]:
                if self.boolean_var_bad.get():
                    self.entry_workout.config(state='normal', bg=bg)
                else:
                    self.entry_workout.config(state='disabled', disabledbackground=bg)
            else:
                self.entry_workout.config(state='normal', bg=bg)
          
    def next(self, event=None):
        global all_variables_current_value_and_workout
        if self.type==PARAMETER_TYPES[2]: # نمیتونه باشه. نوشتم که بدونم بررسی شده. رو محاسباتی ها نمیشه اینتر زد.
            pass
        elif self.type==PARAMETER_TYPES[1]:
            try:
                self.workout = self.entry_workout.get().strip()
                self.workout = float(self.workout)
                all_variables_current_value_and_workout[self.variable_name].update({
                    'value': self.workout,
                    'workout': self.workout
                }) # برای پارامترهای با مقدار ثابت گفته بود فرقی نداره و برای هر دو تا همین رو ذخیره میکنم.
            except ValueError:
                return
            except TypeError:
                return
            finally:
                self.check_color()
        elif self.type==PARAMETER_TYPES[0]:
            self.a = self.label_previous_counter['text']
            self.b = self.entry_current_counter.get().strip()
            self.workout = self.entry_workout.get().strip()
            try:
                self.a = float(self.a)
                self.b = float(self.b)
                self.workout = float(self.workout)
                all_variables_current_value_and_workout[self.variable_name].update({
                    'value': self.b,
                    'workout': self.workout
                }) # گفته بود در هر صورت چه سالم باشه چه خراب تو ولیو خود مقدار جدید ذخیره بشه و ورک اوت هم همین طور. من هم ایف رو دیگه پاک کردم.
            except ValueError:
                return
            except TypeError:
                return
            finally:
                self.check_color()
        self.update_all_variables_current_value_and_workout()

    def update_all_variables_current_value_and_workout(self):
        global all_variables_current_value_and_workout, all_counter_widgets
        for counter_widget in all_counter_widgets:
            counter_widget:CounterWidget
            if counter_widget.formula != "":
                parameters = get_formula_parameters(counter_widget.formula)
                values = []
                for p in parameters:
                    if p=='b':
                        values.append(counter_widget.b)
                    elif p=='a':
                        values.append(counter_widget.a)
                    else:
                        values.append(round3(float(all_variables_current_value_and_workout.get(p).get('workout'))))
                counter_widget.answer = calculate_fn(counter_widget.formula, parameters, values)
            if counter_widget.type==PARAMETER_TYPES[2]:
                counter_widget.entry_workout.config(text=counter_widget.answer)
            elif counter_widget.type==PARAMETER_TYPES[1]:
                pass
                # لازم نیست کاری بکنیم. چون پارامترهای ثابت با تغییر بقیه تغییر نمیکنند.
                # اگر خودشون تغییر بکنند که همون لحظه با کی ریلیز بایندش کردیم و تغییر میکنه
                # اما تغییر بقیه باعث تغییر پارامتر ثابت نمیشه. پس الکی بررسیش نمیکنیم.
            elif counter_widget.type==PARAMETER_TYPES[0]:
                counter_widget.entry_workout.config(state='normal')
                counter_widget.entry_workout.delete(0, END)
                if counter_widget.boolean_var_bad.get()==False:
                    counter_widget.entry_workout.insert(0, round3(counter_widget.answer))
                    counter_widget.entry_workout.config(state='readonly')
                else:
                    counter_widget.entry_workout.insert(0, round3(counter_widget.workout))
            counter_widget.check_color()

    def update_workout(self, event=None):
        global all_variables_current_value_and_workout
        if event and event.keysym=='Return': # باگ داشت وقتی اینتر میزدیم آپدیت میشد. اما چون دکمه اینتر ول شده بود دوباره میومد این رو صدا میکرد و به هم میزد همون کنتور ویجت رو. به خاطر همین اینتر رو ازش حذف کردم که موقعی که انگشت رو از رو اینتر برداشتیم آپدیت نکنه.
            # حالا اگه رو دکمه کپی میزدیم هیچ ایونتی ارسال نمیشد و این ایف ارور میداد. پس گفتم اگه ایونتی وجود داشت و اینتر بود ریترن کن. در غیر این صورت کارت رو انجام بده.
            return
        if event and event.keysym=='period': # این حالت هم باگ داشت نمیشد داخل ورک اوت تو حالت خرابی نقطه گذاشت. روش های مختلف هر کودوم یه مدل اعصاب خرد کن بود و باگ جدید داشت. این مدل به نظرم کمترین باگ رو داشت اینجا گفتم ریترن کنه
            return
        if self.type==PARAMETER_TYPES[2]:
            # این حالت قرار نیست هیچ وقت اتفاق بیفته. چون ما نمیتونیم آپدیتش کنیم. خود برنامه آپدیت میکنه
            # نوشتم که فقط بدونم اینجا بررسی شده
            return
        elif self.type==PARAMETER_TYPES[1]:
            # تو کنتورهای ثابت میشه مقدار نوشت. ممکنه مقدار اشتباه و یا کم و زیاد نوشته بشه. پس ممکنه ارور بده و باید بررسی بشه. رنگ هم باید بررسی بشه و در صورت لزوم تغییر کنه.
            try:
                self.workout=float(self.entry_workout.get().strip())
            except ValueError:
                # اگه این خط رو نذارم ارور میده چون کلا قسمت اکسپت رو ننوشتم. اما من اینجا گفتم کاری نکنه.
                return
            except TypeError:
                return
            finally:
                self.check_color()
        elif self.type==PARAMETER_TYPES[0]:
            if self.boolean_var_bad.get():
                self.check_color()
            else:
                try:
                    self.b = float(self.entry_current_counter.get().strip())
                    parameters = get_formula_parameters(self.formula)
                    values = []
                    for p in parameters:
                        if p=='b':
                            values.append(self.b)
                        elif p=='a':
                            values.append(self.a)
                        else:
                            values.append(float(all_variables_current_value_and_workout.get(p).get('workout')))
                    self.answer = calculate_fn(self.formula, parameters, values)
                    self.workout = self.answer
                except ValueError:
                    return
                except TypeError:
                    return
                finally:
                    self.check_color()
        self.next()
        self.next()
        # :D
        # اینجا یه بار که تابع نکست رو کال میکردم خودش درست میشد. اما بقیه ها نه. باید رو یکی دیگه کلیک میکردم.
        # هاور هم گذاشتم باید دوبار ماوس رو میبردیم بیرون که خیلی جالب نبود.
        # بهترین راه حل به نظرم این بود که دو بار خودم نکست رو پشت سر هم صدا کنم که هم خودش همون لحظه آپدیت
        # بشه و هم کنتورهایی که بهش وابسته هستند.

    def copy_paste(self, event=None):
        if self.type==PARAMETER_TYPES[0]: # اگه انواع دیگه باشن، بولین ور براشون تعریف نشده و این تابع براشون ارور میده. پس شرط گذاشتم براش.
            self.entry_current_counter.delete(0, END)
            self.entry_current_counter.insert(0, self.label_previous_counter['text'])
            self.update_workout()
    
    def check(self):
        if self.type==PARAMETER_TYPES[0]: # اگه انواع دیگه باشن، بولین ور براشون تعریف نشده و این تابع براشون ارور میده. پس شرط گذاشتم براش.
            if self.boolean_var_bad.get():
                self.checkbutton_bad.config(fg='red')
                self.entry_workout.config(state='normal')
                self.entry_workout.focus_set()
            else:
                self.checkbutton_bad.config(fg=FG)
                self.entry_workout.config(state='readonly')
                self.entry_current_counter.focus_set()
            self.update_workout()


class MyToggleButton(Checkbutton):
    def __init__(self, root, variable: BooleanVar, default='off', *args, bg_frame_on='#333333', bg_frame_off='#333333', bg_lable_on='green', bg_lable_off='red', bg_button_on='green', bg_button_off='red', fg_button_on="white", fg_button_off='black', font=('', 18), text_off='off', text_on='on', sleep=0.005, **kwargs):
        super().__init__(*args, **kwargs)
        self.root=root
        self.variable=variable
        if default=='on':
            self.default='on'
            self.variable.set(True)
        else:
            self.default='off'
            self.variable.set(False)
        self.bg_frame_on=bg_frame_on
        self.bg_frame_off=bg_frame_off
        self.bg_lable_on=bg_lable_on
        self.bg_lable_off=bg_lable_off
        self.bg_button_on=bg_button_on
        self.bg_button_off=bg_button_off
        self.fg_button_on=fg_button_on
        self.fg_button_off=fg_button_off
        self.font=font
        self.text_off=text_off
        self.text_on=text_on
        self.sleep=sleep
        self.frame = Frame(self.root, bg=self.bg_frame_off, width=100, height=30)
        self.label=Label(self.frame, bg=self.bg_lable_off)
        self.button = Button(self.frame, font=self.font, text=self.text_off, bg=bg_button_off, disabledforeground=self.fg_button_off, relief='sunken', bd=6, command=self.toggle)
        self.label.place(relx=0.01, relwidth=0.98, rely=0.05, relheight=0.9)
        self.button.place(relx=0.51, relwidth=0.47, rely=0.07, relheight=0.86)
        if self.variable.get():
            self.frame.config(bg=self.bg_frame_on)
            self.label.config(bg=self.bg_lable_on)
            self.button.config(bg=self.bg_button_on, text=self.text_on, fg=self.fg_button_on, disabledforeground=self.fg_button_on, relief='raised')
            self.button.place(relx=0.02)

    def toggle(self, event=None):
        if self.variable.get():
            self.frame.config(bg=self.bg_frame_off)
            self.label.config(bg=self.bg_lable_off)
            self.button.config(bg=self.bg_button_off, fg=self.fg_button_off, disabledforeground=self.fg_button_off, relief='sunken', text=self.text_off)
            Thread(target=self.move).start()
        else:
            self.frame.config(bg=self.bg_frame_on)
            self.label.config(bg=self.bg_lable_on)
            self.button.config(bg=self.bg_button_on, fg=self.fg_button_on, disabledforeground=self.fg_button_on, relief='raised', text=self.text_on)
            Thread(target=self.move).start()
        self.variable.set(not self.variable.get())
            
    def move(self):
        self.button.config(state='disabled')
        if self.variable.get():
            x=0.51
            while x>=0.01:
                self.button.place(relx=x)
                x-=0.01
                sleep(self.sleep)
                self.frame.update()
        else:
            x=0.02
            while x<=0.52:
                self.button.place(relx=x)
                x+=0.01
                sleep(self.sleep)
                self.frame.update()
        self.button.config(state='normal')
            
    def place(self, *args, **kwargs):
        self.frame.place(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

# def my_tool_tip(frame: LabelFrame, text):
#     temp = frame['text']
#     def enter(event):
#         frame.config(text=text)
#     def leave(event):
#         frame.config(text=temp)
#     frame.bind('<Enter>', enter)
#     frame.bind('<Leave>', leave)
# ############################################### Stackoverflow ###############################################
# class ToolTip(object):
#     def __init__(self, widget):
#         self.widget = widget
#         self.tipwindow = None
#         self.id = None
#         self.x = self.y = 0

#     def showtip(self, text):
#         "Display text in tooltip window"
#         self.text = text
#         if self.tipwindow or not self.text:
#             return
#         x, y, cx, cy = self.widget.bbox("insert")
#         x = x + self.widget.winfo_rootx() + 57
#         y = y + cy + self.widget.winfo_rooty() +27
#         self.tipwindow = tw = Toplevel(self.widget)
#         tw.wm_overrideredirect(1)
#         tw.wm_geometry("+%d+%d" % (x, y))
#         label = Label(tw, text=self.text, justify='left',
#                       background="#ffffe0", relief='solid', borderwidth=1,
#                       font=("tahoma", "8", "normal"))
#         label.pack(ipadx=1)

#     def hidetip(self):
#         tw = self.tipwindow
#         self.tipwindow = None
#         if tw:
#             tw.destroy()

# def create_tool_tip(widget, text):
#     toolTip = ToolTip(widget)
#     def enter(event):
#         toolTip.showtip(text)
#     def leave(event):
#         toolTip.hidetip()
#     widget.bind('<Enter>', enter)
#     widget.bind('<Leave>', leave)