from authentication import *

connection = Connection()
root = Tk()
root.title('صفحه احراز هویت')
root.config(bg=BG)
root.resizable(False, False)
S_WIDTH = root.winfo_screenwidth()
S_HEIGHT = root.winfo_screenheight()
# root.geometry(f"{S_WIDTH//2}x{S_HEIGHT//2}+{S_WIDTH//4}+{S_HEIGHT//5}")
root.geometry(f"+{S_WIDTH//3}+{S_HEIGHT//4}")
create_my_theme() # اول تو ستینگز بود. اما چون پنجره ای ساخته نشده بود یکی جدید میساخت. به خاطر همین تبدیلش کردم به تابع و اونجا نوشتم اما اینجا صداش کردم.
login_form = LoginForm(connection, root)
login_form.grid()
root.mainloop()