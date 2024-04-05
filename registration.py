from tkinter import *
from tkinter import messagebox as msb
from connection import Connection
from functions import hash_password

BG='light blue'
FG='orange'
FONT = ('B Nazanin', 24)
PADX = 10
PADY = 5

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
CNF_GRID = {
    'padx': PADX,
    'pady': PADY+5,
}

class RegistrationForm():
    def __init__(self, connection: Connection, root=Tk):
        self.connection=connection
        self.root = root
        self.frame = Frame(self.root, bg=BG)
        self.label_name = Label(self.frame, text="نام", cnf=CNF_LABEL)
        self.entry_name = Entry(self.frame, cnf=CNF_ENTRY, justify='right')
        self.label_surname = Label(self.frame, text="نام خانوادگی", cnf=CNF_LABEL)
        self.entry_surname = Entry(self.frame, cnf=CNF_ENTRY, justify='right')
        self.label_username = Label(self.frame, text="نام کاربری", cnf=CNF_LABEL)
        self.entry_username = Entry(self.frame, cnf=CNF_ENTRY)
        self.label_password1 = Label(self.frame, text="رمز عبور", cnf=CNF_LABEL)
        self.entry_password1 = Entry(self.frame, cnf=CNF_ENTRY, show='*')
        self.label_password2 = Label(self.frame, text="تکرار رمز عبور", cnf=CNF_LABEL)
        self.entry_password2 = Entry(self.frame, cnf=CNF_ENTRY, show='*')
        self.bv_show_password = BooleanVar(self.frame)
        self.checkbox_show_password = Checkbutton(self.frame, text='نمایش رمز عبور', variable=self.bv_show_password, cnf=CNF_CHB, command=self.show_password)
        self.btn_register = Button(self.frame, text='ایجاد حساب کاربری', cnf=CNF_BTN, command=self.create_account)
        self.btn_back = Button(self.frame, text='بازگشت', cnf=CNF_BTN)
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
        password = hash_password(password1)
        result_message, result = self.connection.create_user(name, surname, username, password)
        if result_message == "ok":
            msb.showinfo("پیام موفقیت", f"نام کاربری {username} با موفقیت ساخته شد")
        else:
            print(result_message)
            msb.showerror("ارور", result_message)


    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

if __name__=="__main__":
    connection = Connection()
    root = Tk()
    root.config(bg=BG)
    root.resizable(False, False)
    s_width = root.winfo_screenwidth()
    s_height = root.winfo_screenheight()
    # root.geometry(f"{s_width//2}x{s_height//2}+{s_width//4}+{s_height//5}")
    root.geometry(f"+{s_width//3}+{s_height//4}")
    rf = RegistrationForm(connection, root)
    rf.grid()
    root.mainloop()