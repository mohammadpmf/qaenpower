from authentication import *
import pymysql
import os


def check_mysql_password(event=None):
    host = entry_host.get().strip()
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    try:
        connection = Connection(host, username, password)
        login_form = LoginForm(connection, root)
        login_form.grid()
        temp_window.destroy()
        root.deiconify()
        if bv_dont_ask_again.get():
            try:
                os.mkdir('files')
            except FileExistsError:
                pass # فولدر خودش وجود داره. چی بهتر از این :)
            f = open(r'files/shared_preferences.json', 'w')
            shared_preferences.update({
                'host': host,
                'username': username,
                'password': password,
                'skip_mysql_password': bv_dont_ask_again.get(),
            })
            dump(shared_preferences, f, indent=4, ensure_ascii=False)
            f.close()
        del host, username, password
    except pymysql.err.OperationalError as error:
        msb.showerror('خطا', f'برقرار نشد mysql ارتباط با\n{error}')


try:
    f = open(r'files/shared_preferences.json', 'r')
    shared_preferences = load(f)
    f.close()
except JSONDecodeError:
    shared_preferences = {
        'host': '127.0.0.1',
        'username': 'root',
        'password': 'root',
        'skip_mysql_password': False,
    }
except FileNotFoundError:
    shared_preferences = {
        'host': '127.0.0.1',
        'username': 'root',
        'password': 'root',
        'skip_mysql_password': False,
    }

root = Tk()
S_WIDTH = root.winfo_screenwidth()
S_HEIGHT = root.winfo_screenheight()
root.title('صفحه احراز هویت')
root.config(bg=BG)
root.resizable(False, False)
root.geometry(f"+{S_WIDTH//3}+{S_HEIGHT//3}")
create_my_theme() # اول تو ستینگز بود. اما چون پنجره ای ساخته نشده بود یکی جدید میساخت. به خاطر همین تبدیلش کردم به تابع و اونجا نوشتم اما اینجا صداش کردم.

# تااینجا باید در هر صورت ساخته بشه. از اینجا به بعد بستگی داره به وضعیت که چه طور باشه
try:
    skip = shared_preferences.get('skip_mysql_password', False)
except AttributeError:
    skip = False
if skip:
    connection = Connection('127.0.0.1', 'root', 'root')
    login_form = LoginForm(connection, root)
    login_form.grid()
else:
    root.withdraw()
    temp_window = Toplevel(root)
    temp_window.resizable(False, False)
    temp_window.protocol('WM_DELETE_WINDOW', root.destroy)
    temp_window.geometry(f"+{S_WIDTH//3}+{S_HEIGHT//3}")
    temp_window.config(bg=BG)
    Label(temp_window, cnf=CNF_LABEL, text=' :mysql هاست', anchor='c').grid(row=1, column=2, sticky='news')
    Label(temp_window, cnf=CNF_LABEL, text=' :mysql نام کاربری', anchor='c').grid(row=2, column=2, sticky='news')
    Label(temp_window, cnf=CNF_LABEL, text=' :mysql پسورد', anchor='c').grid(row=3, column=2, sticky='news')
    entry_host = Entry(temp_window, cnf=CNF_ENTRY)
    entry_username = Entry(temp_window, cnf=CNF_ENTRY)
    entry_password = Entry(temp_window, cnf=CNF_ENTRY, show='*')
    entry_host.insert(0, '127.0.0.1')
    entry_username.insert(0, 'root')
    entry_password.insert(0, 'root')
    entry_host.bind('<Return>', lambda e: entry_username.focus_set())
    entry_username.bind('<Return>', lambda e: entry_password.focus_set())
    entry_password.bind('<Return>', lambda e: check_mysql_password())
    entry_password.focus_set()
    entry_host.grid(row=1, column=1, cnf=CNF_GRID)
    entry_username.grid(row=2, column=1, cnf=CNF_GRID)
    entry_password.grid(row=3, column=1, cnf=CNF_GRID)
    Button(temp_window, cnf=CNF_BTN, text='تایید', command=check_mysql_password, padx=PADX, pady=PADY).grid(row=4, column=2, cnf=CNF_GRID)
    bv_dont_ask_again = BooleanVar(temp_window)
    Checkbutton(temp_window, text='ذخیره', variable=bv_dont_ask_again, cnf=CNF_CHB).grid(row=4, column=1, cnf=CNF_GRID, sticky='w')
    # img_settings = Image.open(r'icons/settings.png')
    # img_settings = img_settings.resize((SETTINGS_ICON_SIZE, SETTINGS_ICON_SIZE))
    # img_settings = ImageTk.PhotoImage(img_settings)
    # Button(temp_window, cnf=CNF_BTN, image=img_settings, command=None, padx=PADX, pady=PADY).grid(row=4, column=1, cnf=CNF_GRID, sticky='w')

root.mainloop()