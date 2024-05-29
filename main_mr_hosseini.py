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
Label(temp_window, cnf=CNF_LABEL, text='mysql host: ', anchor='w').grid(row=1, column=1, sticky='news')
Label(temp_window, cnf=CNF_LABEL, text='mysql username: ', anchor='w').grid(row=2, column=1, sticky='news')
Label(temp_window, cnf=CNF_LABEL, text='mysql password: ', anchor='w').grid(row=3, column=1, sticky='news')
entry_host = Entry(temp_window, cnf=CNF_ENTRY)
entry_username = Entry(temp_window, cnf=CNF_ENTRY)
entry_password = Entry(temp_window, cnf=CNF_ENTRY, show='*')
entry_host.insert(0, '127.0.0.1')
entry_username.insert(0, 'root')
entry_password.insert(0, 'root')
entry_host.bind('<Return>', entry_username.focus_set)
entry_username.bind('<Return>', entry_password.tk_focusFollowsMouse)
entry_password.bind('<Return>', check_mysql_password)
entry_password.focus_set()
entry_host.grid(row=1, column=2, cnf=CNF_GRID)
entry_username.grid(row=2, column=2, cnf=CNF_GRID)
entry_password.grid(row=3, column=2, cnf=CNF_GRID)
Button(temp_window, cnf=CNF_BTN, text='تایید', command=check_mysql_password, padx=PADX, pady=PADY).grid(row=4, column=1, cnf=CNF_GRID)
root.mainloop()