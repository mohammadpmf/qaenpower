from ui_settings import *
from PIL import Image, ImageTk
from connection import Connection
from functions import calculate_fn, get_formula_parameters, what_is_variable_name_problem, what_is_formula_problem, get_jnow, round3, jdatetime
from models import Staff, Counter
from ui_settings import Tk


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
        self.user = user
        self.main_window = Toplevel(self.frame)
        self.main_window.title(f'حساب کاربری {self.user}')
        self.main_window.config(bg=BG)
        # self.main_window.resizable(False, False)
        self.main_window.geometry(f"+{S_WIDTH//4}+0")
        self.main_window.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.tab_control = ttk.Notebook(self.main_window) 
        self.tab_control.pack(anchor='n')
        self.frame_change_password_tab = Frame(self.tab_control, bg=BG)
        self.frame_add_statistics_tab = Frame(self.tab_control, bg=BG)
        self.tab_control.add(self.frame_change_password_tab, text ='تغییر رمز عبور')
        self.tab_control.add(self.frame_add_statistics_tab, text ='ثبت آمار')
        if self.user.access_level==1:
            self.frame_add_part_tab = Frame(self.tab_control, bg=BG)
            self.frame_add_place_tab = Frame(self.tab_control, bg=BG)
            self.frame_all_counters_tab = Frame(self.tab_control, bg=BG)
            self.frame_add_counter_tab = Frame(self.tab_control, bg=BG)
            self.frame_add_user_tab = Frame(self.tab_control, bg=BG)
            self.tab_control.add(self.frame_add_user_tab, text ='افزودن کاربر جدید')
            self.tab_control.add(self.frame_add_counter_tab, text ='افزودن پارامتر جدید')
            self.tab_control.add(self.frame_all_counters_tab, text ='پارامترهای موجود')
            self.tab_control.add(self.frame_add_place_tab, text ='افزودن مکان جدید')
            self.tab_control.add(self.frame_add_part_tab, text ='افزودن بخش جدید')
        self.tab_control.select(self.frame_add_statistics_tab)

        ###################################### frame_add_statistics ######################################
        self.frame_add_statistics = Frame(self.frame_add_statistics_tab, bg=BG)
        self.frame_add_statistics.pack(side=RIGHT)
        self.date_picker_frame = Frame(self.frame_add_statistics)
        self.date_picker_frame.pack(side=TOP, expand=True, fill='x')
        self.tab_control_frame = ttk.Notebook(self.frame_add_statistics)
        self.tab_control_frame.pack(side=RIGHT, expand=True, fill='both')
        self.date_picker = DatePicker(self.root, self.date_picker_frame)
        self.date_picker.pack(side=RIGHT, expand=True, fill='both')
        self.seed_tabs_of_parts()

        ###################################### frame_change_users_password ######################################
        self.frame_change_users_password = Frame(self.frame_change_password_tab, bg=BG)
        self.frame_change_users_password.pack(side=RIGHT)
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

        ############################################## frame_user ##############################################
        self.frame_user = Frame(self.frame_add_user_tab, bg=BG)
        self.frame_user.pack(side=RIGHT)
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
        self.frame_counter.pack(side=RIGHT)
        self.label_counter_part = Label(self.frame_counter, text="بخش پارامتر", cnf=CNF_LABEL)
        self.entry_counter_part = ttk.Combobox(self.frame_counter, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')
        self.entry_counter_part.bind("<<ComboboxSelected>>", self.show_places_of_this_part)
        self.label_counter_place = Label(self.frame_counter, text="مکان پارامتر", cnf=CNF_LABEL)
        self.entry_counter_place = ttk.Combobox(self.frame_counter, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')
        self.label_counter_name = Label(self.frame_counter, text="نام پارامتر", cnf=CNF_LABEL)
        self.entry_counter_name = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER, justify='right')
        self.label_counter_type = Label(self.frame_counter, text="نوع پارامتر", cnf=CNF_LABEL)
        self.entry_counter_type = ttk.Combobox(self.frame_counter, values=COUNTER_TYPES, font=FONT, width=WORDS_WIDTH, justify='center')
        self.entry_counter_type.insert(0, COUNTER_TYPES[0])
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
        self.label_counter_alarm_lower_bound = Label(self.frame_counter, text="حد پایین خطر", cnf=CNF_LABEL)
        self.entry_counter_alarm_lower_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.label_counter_alarm_upper_bound = Label(self.frame_counter, text="حد بالای خطر", cnf=CNF_LABEL)
        self.entry_counter_alarm_upper_bound = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.label_counter_formula = Label(self.frame_counter, text="فرمول", cnf=CNF_LABEL)
        self.entry_counter_formula = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.label_counter_formula_parameters = Label(self.frame_counter, text="متغیرهای فرمول", cnf=CNF_LABEL)
        self.entry_counter_formula_parameters = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER)
        self.btn_counter_register = Button(self.frame_counter, text='ایجاد پارامتر', cnf=CNF_BTN, command=self.create_counter)
        self.btn_counter_update = Button(self.frame_counter, text='ویرایش پارامتر', cnf=CNF_BTN, command=self.update_counter)
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
        self.entry_counter_formula_parameters.bind('<Return>', self.create_counter)

        ############################################# frame_part #############################################
        self.frame_part = Frame(self.frame_add_part_tab, bg=BG)
        self.frame_part.pack(side=RIGHT)
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
        self.frame_place.pack(side=RIGHT)
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
        self.frame_all_counters.pack(side=RIGHT)
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
        self.treev_all_counters.column("1", width = 200, anchor ='c')
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
        for place_id, place_title, place_part, place_sort in places:
            values.append(place_title)
        self.entry_counter_place.config(state='normal', values=values)
        self.entry_counter_place.delete(0, END)
        self.entry_counter_place.config(state='readonly')

    # تابعی برای این که وقتی نوع پارامتر انتخاب شد، کمبو باکس نوع مقدار پیش فرض تغییر کنه
    # و همچنین بعضی از باکس ها فعال یا غیر فعال بشن
    def check_counter_type(self, event=None):
        counter_type = self.entry_counter_type.get()
        self.entry_counter_default_value.config(state='normal')
        self.entry_counter_default_value.delete(0, END)
        if counter_type in COUNTER_TYPES[0:2]: # یعنی یا کنتور معمولی باشه یا ثابت
            self.entry_counter_default_value.insert(0, DEFAULT_VALUES[0])
            self.entry_counter_default_value.config(values=DEFAULT_VALUES)
        elif counter_type==COUNTER_TYPES[2]: # یعنی از نوع محاسباتی باشه
            self.entry_counter_default_value.config(values=[])
        self.entry_counter_default_value.config(state='readonly')
        if counter_type==COUNTER_TYPES[1]: # fixed:
            self.entry_counter_formula.delete(0, END)
            self.entry_counter_formula.config(state='readonly')
            self.entry_counter_formula_parameters.delete(0, END)
            self.entry_counter_formula_parameters.config(state='readonly')
        else:
            self.entry_counter_formula.config(state='normal')
            self.entry_counter_formula_parameters.config(state='normal')

    # تابعی جهت ایجاد پارامتر
    def create_counter(self, event=None):
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
        counters_variable_names = self.connection.get_all_counters_variable_names()
        problem = what_is_variable_name_problem(variable_name, counters_variable_names)
        if problem:
            msb.showwarning("هشدار", problem)
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
                msb.showwarning("هشدار", "لطفا حد پایین خطر را به صورت عددی وارد کنید")
                self.entry_counter_alarm_lower_bound.focus_set()
                return
        if alarm_upper_bound == "":
            alarm_upper_bound=None
        else:
            try:
                alarm_upper_bound = float(alarm_upper_bound)
            except:
                msb.showwarning("هشدار", "لطفا حد بالای خطر را به صورت عددی وارد کنید")
                self.entry_counter_alarm_upper_bound.focus_set()
                return
        if formula != "":
            result = what_is_formula_problem(formula, formula_parameters, variable_name, counters_variable_names)
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
                    result = what_is_formula_problem(formula, ' '.join(result), variable_name, counters_variable_names)
                    if isinstance(result, list):
                        is_everything_ok=True
                    else:
                        is_everything_ok=False
                        msb.showwarning('هشدار', result)
        if formula == "" and type in [COUNTER_TYPES[0], COUNTER_TYPES[2]]:
            msb.showwarning("هشدار", "برای پارامترهای محاسباتی و کنتور، فرمول نمیتواند خالی باشد")
            self.entry_counter_formula.focus_set()
            return
        if is_everything_ok:
            result_message, _ = self.connection.create_counter(name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place)
        else:
            return
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"پارامتر {name} با موفقیت در مکان {place} از بخش {part} ساخته شد")
            self.refresh_ui()
        else:
            msb.showerror("خطا", result_message)
            print(_)

    # تابعی جهت ویرایش پارامتر
    def update_counter(self):
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
        this_counter = self.connection.get_counter_by_variable_name(variable_name)
        if this_counter == None:
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
                msb.showwarning("هشدار", "لطفا حد پایین خطر را به صورت عددی وارد کنید")
                self.entry_counter_alarm_lower_bound.focus_set()
                return
        if alarm_upper_bound == "":
            alarm_upper_bound=None
        else:
            try:
                alarm_upper_bound = float(alarm_upper_bound)
            except:
                msb.showwarning("هشدار", "لطفا حد بالای خطر را به صورت عددی وارد کنید")
                self.entry_counter_alarm_upper_bound.focus_set()
                return
        if formula != "":
            counters_variable_names = self.connection.get_all_counters_variable_names()
            result = what_is_formula_problem(formula, formula_parameters, variable_name, counters_variable_names)
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
                    result = what_is_formula_problem(formula, ' '.join(result), variable_name, counters_variable_names)
                    if isinstance(result, list):
                        is_everything_ok=True
                    else:
                        is_everything_ok=False
                        msb.showwarning('هشدار', result)
        if formula == "" and type in [COUNTER_TYPES[0], COUNTER_TYPES[2]]:
            msb.showwarning("هشدار", "برای پارامترهای محاسباتی و کنتور، فرمول نمیتواند خالی باشد")
            self.entry_counter_formula.focus_set()
            return
        if is_everything_ok:
            result_message, _ = self.connection.update_counter(name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place, this_counter.previous_value, this_counter.current_value)
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
        temp_counter = self.connection.get_counter_by_id(id)
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
        for part_id, part_name, part_order in parts:
            values.append(part_name)
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
            self.treev_part.insert("", i, text=part[0], values=(part[1], i+1))
    
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
            self.treev_place.insert("", i, text=place[0], values=(place[1], i+1))
               
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
                print(id, order)
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
            result_message, _ = self.connection.change_counters_order(id, order)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"ترتیب کنتور ها با موفقیت تغییر یافت")
            self.refresh_ui()
        else:
            msb.showerror("خطا", result_message)
            print(_)

    def refresh_all_counters_treeview(self):
        self.treev_all_counters.delete(*self.treev_all_counters.get_children())
        counters = self.connection.get_all_counters_short_info()
        for i, counter in enumerate(counters):
            self.treev_all_counters.insert("", i, text=counter[0], values=(*(counter[1:]), i+1))

    ######################################### add statistics functions ######################################
    # تابعی برای این که تب های درون قسمت آمار پارامتر ها رو مقداردهی کنه
    def seed_tabs_of_parts(self):
        for item in self.tab_control_frame.winfo_children():
            item.destroy()
        tabs_list = []
        parts_tab = []
        places_with_counters = []
        parts=self.connection.get_all_parts()
        for i, part in enumerate(parts):
            places_with_counters.clear()
            tabs_list.append(ttk.Frame(self.tab_control_frame))
            tabs_list[i].pack()
            self.tab_control_frame.add(tabs_list[i], text =f'بخش {part[1]}')
            temp_places=self.connection.get_all_places_by_part_id(part[0])
            for place in temp_places:
                counters = self.connection.get_all_counters_of_this_part_and_place(part_id=place[2], place_id=place[0])
                places_with_counters.append(counters)
            parts_tab.append(PartWidget(self.connection, tabs_list[i], places_with_counters))
            # parts[i].grid(row=1, column=1)
            parts_tab[i].pack()
            # parts[i].place(width=1024, height=400)
        self.tab_control_frame.pack(expand = 1, fill ="both")

    ########################################### generic functions ###########################################
    # تابعی جهت برگشتن به صفحه احراز هویت از برنامه
    def back(self, event=None):
        self.main_window.destroy()
        self.root.deiconify()

    def refresh_ui(self):
        self.refresh_parts_tree_view()
        self.refresh_parts_values_in_comboboxes()
        # self.refresh_places_tree_view() # این ورودی میخواد. به خاطر همین کامنت کردم. گذاشتم که بعدا اشتباهی دوباره نذارمش.
        self.refresh_places_frame_after_selecting_part()
        self.refresh_all_counters_treeview()
        self.seed_tabs_of_parts()



class DatePicker(MyWindows):
    days_list = [i for i in range(1, 32)]
    months_list = [i for i in range(1, 13)]
    years_list = [i for i in range(1400, 1410)]
    def __init__(self, connection: Connection, root: Tk):
        super().__init__(connection, root)
        self.year = StringVar(self.frame)
        self.month = StringVar(self.frame)
        self.day = StringVar(self.frame)
        self.year.set('سال')
        self.month.set('ماه')
        self.day.set('روز')
        self.btn_yesterday = Button(self.frame, text='روز قبل', cnf=CNF_BTN, font=FONT3, padx=0, pady=0, command=lambda: self.time_delta(-1))
        self.btn_tomorrow = Button(self.frame, text='روز بعد', cnf=CNF_BTN, font=FONT3, padx=0, pady=0, command=lambda: self.time_delta(1))
        self.combo_year = ttk.Combobox(self.frame, values=self.years_list, textvariable=self.year, width=7, state='readonly', font=FONT, justify='center')
        self.combo_month = ttk.Combobox(self.frame, values=self.months_list, textvariable=self.month, width=5, state='readonly', font=FONT, justify='center')
        self.combo_day = ttk.Combobox(self.frame, values=self.days_list, textvariable=self.day, width=5, state='readonly', font=FONT, justify='center')
        self.combo_year.bind("<<ComboboxSelected>>", self.check_date)
        self.combo_month.bind("<<ComboboxSelected>>", self.check_date)
        self.combo_day.bind("<<ComboboxSelected>>", self.check_date)
        self.label_date = Label(self.frame, text="!!! تاریخ نامعتبر !!!", cnf=CNF_LABEL, pady=32, width=20)
        self.btn_confirm = Button(self.frame, text="تایید تاریخ", cnf=CNF_BTN, font=FONT2, padx=0, pady=0, command=self.confirm)
        self.btn_yesterday.pack(cnf=CNF_PACK2)
        self.combo_day.pack(cnf=CNF_PACK2)
        self.combo_month.pack(cnf=CNF_PACK2)
        self.combo_year.pack(cnf=CNF_PACK2)
        self.btn_tomorrow.pack(cnf=CNF_PACK2)
        self.label_date.pack(cnf=CNF_PACK2)
        self.refresh_date()

    def time_delta(self, days):
        try:
            jdate = jdatetime.date(int(self.combo_year.get()), int(self.combo_month.get()), int(self.combo_day.get()))
            d = jdatetime.timedelta(days=days)
            new_date = jdate + d
            self.refresh_date(new_date)
        except ValueError:
            msb.showerror('', "تاریخ به درستی انتخاب نشده است")
            pass

    def refresh_date(self, date=None):
        if date==None:
            date=get_jnow()
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
            if y=='سال' or m=='ماه' or d=='روز':
                return
            else:
                date = jdatetime.date(int(y), int(m), int(d))
                temp = f"{'تاریخ':10} {WEEKDAYS.get(date.weekday())} {d} {MONTH_NAMES.get(int(m))} {y}"
                self.label_date.config(text=temp)
                self.btn_confirm.pack(cnf=CNF_PACK2)
        except ValueError:
            temp = "!!! تاریخ نامعتبر !!!"
            self.label_date.config(text=temp)
            self.btn_confirm.pack_forget()

    def confirm(self):
        date = self.label_date['text'] 
        print(date)


class PartWidget(MyWindows):
    def __init__(self, connection: Connection, root: Tk, places_with_counters):
        super().__init__(connection, root)
        self.places_with_counters=places_with_counters # یک لیستی از مکان ها با پارامترهایی که داخلشون هست. یعنی یک لیستی از تاپل ها که هر کودوم از تاپل ها هر عضوشون یه پارامتر هست.
        self.my_canvas = Canvas(self.frame, width=S_WIDTH*1, height=S_HEIGHT*1, bg=BG)
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
        self.places_window = Frame(self.my_canvas)
        self.my_canvas.create_window((0, 0), window=self.places_window, anchor="ne")
        # all_counters = [] # برای بایند کردن تعریف کرده بودم که فعلا کاری نکردم.
        # print(all_counters)
        for i, counters in enumerate(self.places_with_counters):
            if counters: # یعنی اگر یک مکان پارامتر هایی داشت این کارها رو انجام بده اگه نداشت الکی ردیف براش درست نکنه
                self.frame_row = Frame(self.places_window, bg=BG)
                for index in range(994, 1000):
                    self.frame_row.columnconfigure(index=index, weight=1, minsize=190)
                self.frame_row.columnconfigure(index=1000, weight=1, minsize=120)
                self.frame_row.grid()
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
                        previous_value=counter.previous_value,
                        current_value=counter.current_value,
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
                        font=FONT2)
                    # all_counters.append(c)
                    c.grid(row=i, column=1000-1-j, sticky='news', padx=4, pady=2)
        # print(all_counters)


class CounterWidget(Counter, MyWindows):
    def __init__(self, connection: Connection, root: Tk, part, place, name, variable_name, previous_value=0, current_value=0, formula='', type='کنتور', default_value=0, unit=None, warning_lower_bound=None, warning_upper_bound=None, alarm_lower_bound=None, alarm_upper_bound=None, id=None, place_title=None, *args, **kwargs):
        super().__init__(part, place, name, variable_name, previous_value, current_value, formula, type, default_value, unit, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, id, place_title)
        MyWindows.__init__(self, connection, root)
        if self.formula != "":
            parameters = get_formula_parameters(formula)
            values = []
            for p in parameters:
                if p=='b':
                    values.append(self.current_value)
                elif p=='a':
                    values.append(self.previous_value)
                else:
                    values.append(self.connection.get_current_value_of_counter_by_variable_name(p))
            answer = calculate_fn(formula, parameters, values)
        self.frame = LabelFrame(self.root, text=f"پارامتر {self.name}", cnf=CNF_LBL_FRM, padx=PADX, pady=PADY, labelanchor='n', bg=BG, fg=FG, *args, **kwargs)
        if self.type==COUNTER_TYPES[0]:
            self.img = Image.open('copy-icon.png')
            self.img = self.img.resize((COPY_ICON_SIZE, COPY_ICON_SIZE))
            self.img = ImageTk.PhotoImage(self.img)
            self.btn_copy = Button(self.frame, image=self.img, cnf=CNF_BTN2, command=self.copy_down, *args, **kwargs)
            self.entry_current_counter = Entry(self.frame, cnf=CNF_ENTRY2, width=WORDS_WIDTH2, *args, **kwargs)
            if self.default_value==DEFAULT_VALUES[0]:
                self.entry_current_counter.insert(0, round3(self.current_value))
            elif self.default_value==DEFAULT_VALUES[1]:
                self.entry_current_counter.insert(0, DEFAULT_VALUES[1])
            elif self.default_value==DEFAULT_VALUES[2]:
                self.entry_current_counter.delete(0, END)
            self.entry_previous_counter = Label(self.frame, cnf=CNF_LBL2, text=round3(self.current_value), *args, **kwargs)
            self.entry_workout = Entry(self.frame, cnf=CNF_ENTRY2, width=WORDS_WIDTH3, *args, **kwargs)
            self.entry_workout.insert(0, 'کارکرد')
            self.entry_workout.config(state='readonly')
            self.boolean_var_bad = BooleanVar(self.frame)
            self.checkbutton_bad = Checkbutton(self.frame, cnf=CNF_CHB2, variable=self.boolean_var_bad, text='خرابی', command=self.check)
            self.entry_workout.bind('<Return>', self.confirm)
            self.entry_workout.bind('<KeyRelease>', self.check_color)
            self.entries = [self.entry_previous_counter, self.entry_current_counter, self.entry_workout] # میخواستم برای دیسبل کردن و اینیبل کردن یه حلقه بزنم. همه شون رو ریختم تو یه لیست داخل آبجکت که تو تابع چک کارم راحت تر بشه.
            self.entry_workout.grid(row=2, column=1, cnf=CNF_GRID2)
            self.entry_current_counter.grid(row=2, column=2, cnf=CNF_GRID2)
            self.btn_copy.grid(row=2, column=3, cnf=CNF_GRID2)
            self.checkbutton_bad.grid(row=3, column=1, cnf=CNF_GRID2)
            self.entry_previous_counter.grid(row=3, column=2, columnspan=2, cnf=CNF_GRID2)
        elif self.type==COUNTER_TYPES[1]:
            self.entry_current_counter = Entry(self.frame, cnf=CNF_ENTRY2, width=25, *args, **kwargs)
            if self.default_value==DEFAULT_VALUES[0]:
                self.entry_current_counter.insert(0, round3(self.previous_value))
            elif self.default_value==DEFAULT_VALUES[1]:
                self.entry_current_counter.insert(0, DEFAULT_VALUES[1])
            elif self.default_value==DEFAULT_VALUES[2]:
                self.entry_current_counter.delete(0, END)
            self.entry_current_counter.grid(row=1, column=1, cnf=CNF_GRID2)
        elif self.type==COUNTER_TYPES[2]:
            self.entry_current_counter = Label(self.frame, text=answer, cnf=CNF_LBL2, width=17, *args, **kwargs)
            self.entry_current_counter.grid(row=1, column=1, cnf=CNF_GRID2)
        self.entry_current_counter.bind('<Return>', self.confirm)
        self.entry_current_counter.bind('<KeyRelease>', self.update_workout)
   
    def confirm(self, event=None):
        value = self.entry_current_counter.get()
        try:
            value = float(value)
        except:
            msb.showwarning("هشدار", "مقدار باید به صورت عدد صحیح یا اعشاری باشد")
            return
        result_message, ـ = self.connection.create_counter_log(value, self.id)
        result_message, ـ = self.connection.update_counter_usage(value, self.id)
        if result_message == "ok":
            msb.showinfo("پیام موفقیت", f"مقدار {value} با موفقیت برای پارامتر {self.name} از مکان {self.place_title} ثبت شد.")
        else:
            msb.showerror("ارور", result_message)

    def update_workout(self, event=None):
        if self.type==COUNTER_TYPES[0] and (event.keysym in '0123456789' or event.keysym in ['period', 'BackSpace']):
            try:
                current = float(self.entry_current_counter.get().strip())
                prev = float(self.entry_previous_counter['text'])  # میشه از دیتابیس گرفت که دقیق تر باشه. اما من نگرفتم و از رو همون ۳ رقم اعشار خووندم.
                workout = current - prev
                workout = round3(workout)
            except:
                workout = f"-{self.entry_previous_counter['text']}"
                return
            finally:
                self.entry_workout.config(state='normal')
                self.entry_workout.delete(0, END)
                self.entry_workout.insert(0, workout)
                self.entry_workout.config(state='readonly')
                self.check_color()

    def copy_down(self):
        self.boolean_var_bad.set(False)
        self.check()
        self.entry_current_counter.delete(0, END)
        self.entry_current_counter.insert(0, self.entry_previous_counter['text'])
        self.entry_workout.config(state='normal')
        self.entry_workout.delete(0, END)
        self.entry_workout.insert(0, 0)
        self.entry_workout.config(state='readonly')
        self.check_color()
    
    def check(self):
        if self.boolean_var_bad.get():
            self.entry_current_counter.config(state='readonly')
            self.entry_previous_counter.config(state='disabled', bg=DISABLED_BG)
            self.entry_workout.config(state='normal')
            if self.entry_workout.get()=='کارکرد':
                self.entry_workout.delete(0, END)
            self.entry_workout.focus_set()
        else:
            self.entry_workout.config(state='readonly')
            self.entry_current_counter.config(state='normal')
            self.entry_previous_counter.config(state='normal', bg=BG)
            self.entry_current_counter.focus_set()
        for entry in self.entries:
            if entry['state']=='normal':
                entry.config(fg=FG)
            else:
                entry.config(fg=DISABLED_FG)
        self.check_color()

    def check_color(self, event=None):
        w_l = self.warning_lower_bound
        w_u = self.warning_upper_bound
        a_l = self.alarm_lower_bound
        a_u = self.alarm_upper_bound
        try:
            workout = float(self.entry_workout.get())
            if workout<=a_l:
                bg = ALARM_COLOR
            elif workout<=w_l:
                bg = WARNING_COLOR
            elif workout>=a_u:
                bg = ALARM_COLOR
            elif workout>=w_u:
                bg = WARNING_COLOR
            else:
                bg=BG
            self.entry_workout.config(state='normal', bg=bg)
        except:
            pass