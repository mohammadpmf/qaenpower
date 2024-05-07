from ui_settings import *
from connection import Connection
from functions import what_is_variable_name_problem, what_is_formula_problem


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
        self.label_counter_part = Label(self.frame_counter, text="بخش کنتور", cnf=CNF_LABEL)
        self.entry_counter_part = ttk.Combobox(self.frame_counter, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')
        self.entry_counter_part.bind("<<ComboboxSelected>>", self.show_places_of_this_part)
        self.label_counter_place = Label(self.frame_counter, text="مکان کنتور", cnf=CNF_LABEL)
        self.entry_counter_place = ttk.Combobox(self.frame_counter, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')

        self.label_counter_name = Label(self.frame_counter, text="نام کنتور", cnf=CNF_LABEL)
        self.entry_counter_name = Entry(self.frame_counter, cnf=CNF_ENTRY_COUNTER, justify='right')
        self.label_counter_type = Label(self.frame_counter, text="نوع کنتور", cnf=CNF_LABEL)
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
        self.btn_counter_register = Button(self.frame_counter, text='ایجاد کنتور', cnf=CNF_BTN, command=self.create_counter)
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
        self.btn_counter_back.grid(row=17, column=5, cnf=CNF_GRID)
        self.entry_counter_name.bind('<Return>', lambda e: self.entry_counter_type.focus_set())
        self.entry_counter_type.bind('<Return>', lambda e: self.entry_counter_unit.focus_set())
        self.entry_counter_unit.bind('<Return>', lambda e: self.entry_counter_default_value.focus_set())
        self.entry_counter_default_value.bind('<Return>', lambda e: self.entry_counter_variable_name.focus_set())
        self.entry_counter_variable_name.bind('<Return>', lambda e: self.entry_counter_warning_lower_bound.focus_set())
        self.entry_counter_warning_lower_bound.bind('<Return>', lambda e: self.entry_counter_warning_upper_bound.focus_set())
        self.entry_counter_warning_upper_bound.bind('<Return>', lambda e: self.entry_counter_alarm_lower_bound.focus_set())
        self.entry_counter_alarm_lower_bound.bind('<Return>', lambda e: self.entry_counter_alarm_upper_bound.focus_set())
        self.entry_counter_alarm_upper_bound.bind('<Return>', lambda e: exit())

        # frame_part
        self.frame_part = Frame(self.frame_add_part, bg=BG)
        self.frame_part.place(relx=0.2, rely=0.04, relwidth=1, relheight=1)
        self.label_part_name = Label(self.frame_part, text="نام بخش", cnf=CNF_LABEL)
        self.entry_part_name = Entry(self.frame_part, cnf=CNF_ENTRY_COUNTER, justify='right')
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

        # frame_place
        self.frame_place = Frame(self.frame_add_place, bg=BG)
        self.frame_place.place(relx=0.15, rely=0.04, relwidth=1, relheight=1)
        self.label_place_part_name = Label(self.frame_place, text="نام بخش", cnf=CNF_LABEL)
        self.entry_place_part_name = ttk.Combobox(self.frame_place, font=FONT, width=WORDS_WIDTH, justify='center', state='readonly')
        self.entry_place_part_name.bind("<<ComboboxSelected>>", self.refresh_places_frame_after_selecting_part)
        self.label_place_name = Label(self.frame_place, text="نام مکان", cnf=CNF_LABEL)
        self.entry_place_name = Entry(self.frame_place, cnf=CNF_ENTRY_COUNTER, justify='right', state='readonly')
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

    def refresh_parts_tree_view(self):
        self.treev_part.delete(*self.treev_part.get_children())
        parts = self.connection.get_all_parts()
        for i, part in enumerate(parts):
            self.treev_part.insert("", i, text=part[0], values=(part[1], i+1))
    
    def refresh_places_tree_view(self, part_id):
        self.treev_place.delete(*self.treev_place.get_children())
        places = self.connection.get_all_places_by_part_id(part_id)
        for i, place in enumerate(places):
            self.treev_place.insert("", i, text=place[0], values=(place[1], i+1))
               
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

    def confirm_tree_place(self):
        for item in self.treev_place.get_children():
            item = self.treev_place.item(item)
            print(item)
            id=int(item['text'])
            order=int(item['values'][-1])
            print(id, order)
            result_message, _ = self.connection.change_places_order(id, order)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"ترتیب مکان ها با موفقیت تغییر یافت")
        else:
            msb.showerror("خطا", result_message)
            print(_)

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
    
    def confirm_tree_part(self):
        for item in self.treev_part.get_children():
            item = self.treev_part.item(item)
            id=int(item['text'])
            order=int(item['values'][-1])
            result_message, _ = self.connection.change_parts_order(id, order)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"ترتیب بخش ها با موفقیت تغییر یافت")
        else:
            msb.showerror("خطا", result_message)
            print(_)


    def show_places_of_this_part(self, event=None):
        part_name = self.entry_counter_part.get()
        part_id, part_name = self.connection.get_part_by_title(part_name)
        places = self.connection.get_all_places_by_part_id(part_id)
        values = []
        for place_id, place_title, place_part in places:
            values.append(place_title)
        self.entry_counter_place.config(state='normal', values=values)
        self.entry_counter_place.delete(0, END)
        self.entry_counter_place.config(state='readonly')
    
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
            msb.showwarning("هشدار", "کنتور مربوط به کدام بخش است؟")
            self.entry_counter_part.focus_set()
            return
        if place == "":
            msb.showwarning("هشدار", "کنتور مربوط به کدام مکان است؟")
            self.entry_counter_place.focus_set()
            return
        if name == "":
            msb.showwarning("هشدار", "نام کنتور را وارد کنید")
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
        if formula == "" and type in [COUNTER_TYPES[0], COUNTER_TYPES[2]]:
            msb.showwarning("هشدار", "برای کنتورهای محاسباتی و معمولی، فرمول نمیتواند خالی باشد")
            self.entry_counter_formula.focus_set()
            return
        problem = what_is_formula_problem(formula, formula_parameters, counters_variable_names, self.connection)
        if problem:
            msb.showwarning("هشدار", problem)
            self.entry_counter_formula.focus_set()
            return
        result_message, _ = self.connection.create_counter(name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"کنتور {name} با موفقیت در مکان {place} از بخش {part} ساخته شد")
        else:
            msb.showerror("خطا", result_message)
            print(_)

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

    # part functions
    def create_part(self):
        title = self.entry_part_name.get().strip()
        if title=="":
            msb.showwarning("هشدار", "نام بخش نمیتواند خالی باشد.")
            return
        result_message, _ = self.connection.create_part(title)
        if result_message=='ok':
            msb.showinfo("پیام موفقیت", f"بخش {title} با موفقیت ساخته شد.")
            self.refresh_parts_values_in_comboboxes()
            self.refresh_parts_tree_view()
        else:
            msb.showerror("خطا", result_message)
            print(_)

    def refresh_parts_values_in_comboboxes(self, event=None):
        parts = self.connection.get_all_parts()
        values = []
        for part_id, part_name, part_order in parts:
            values.append(part_name)
        self.entry_place_part_name.config(state='normal', values=values)
        self.entry_place_part_name.config(state='readonly')
        self.entry_counter_part.config(state='normal', values=values)
        self.entry_counter_part.config(state='readonly')

    # place functions
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

    def create_place(self):
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
        else:
            msb.showerror("خطا", result_message)
            print(_)



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
