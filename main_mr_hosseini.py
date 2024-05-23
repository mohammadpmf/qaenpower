from authentication import *
import pymysql


def check_mysql_password(event=None):
    p = entry_password.get()
    try:
        connection = Connection(password=p)
        create_my_theme() # اول تو ستینگز بود. اما چون پنجره ای ساخته نشده بود یکی جدید میساخت. به خاطر همین تبدیلش کردم به تابع و اونجا نوشتم اما اینجا صداش کردم.
        login_form = LoginForm(connection, root)
        login_form.grid()
        del p
        temp_window.destroy()
        root.deiconify()
    except pymysql.err.OperationalError as error:
        msb.showerror('خطا', 'برقرار نشد mysql ارتباط با')


root = Tk()
S_WIDTH = root.winfo_screenwidth()
S_HEIGHT = root.winfo_screenheight()
root.title('صفحه احراز هویت')
root.resizable(False, False)
root.geometry(f"+{S_WIDTH//3}+{S_HEIGHT//3}")
root.withdraw()
temp_window = Toplevel(root)
temp_window.resizable(False, False)
temp_window.protocol('WM_DELETE_WINDOW', root.destroy)
temp_window.geometry(f"+{S_WIDTH//3}+{S_HEIGHT//3}")
temp_window.config(bg=BG)
Label(temp_window, cnf=CNF_LABEL, text=': را وارد کنید mysql پسورد').grid(row=1, column=2)
entry_password = Entry(temp_window, cnf=CNF_ENTRY, show='*')
entry_password.grid(row=1, column=1)
entry_password.insert(0, 'root')
entry_password.bind('<Return>', check_mysql_password)
entry_password.focus_set()
Button(temp_window, cnf=CNF_BTN, text='تایید', width=16, command=check_mysql_password).grid(row=2, column=1, columnspan=2)
root.mainloop()