from authentication import *

connection = Connection()


############################################## root ##############################################
root = Tk()
root.title('صفحه احراز هویت')
root.config(bg=BG)
root.resizable(False, False)
s_width = root.winfo_screenwidth()
s_height = root.winfo_screenheight()
# root.geometry(f"{s_width//2}x{s_height//2}+{s_width//4}+{s_height//5}")
root.geometry(f"+{s_width//3}+{s_height//4}")



############################################## admin_window ##############################################
admin_window = Toplevel(root)
admin_window.title('صفحه مدیریت')
admin_window.config(bg=BG)
admin_window.resizable(False, False)
# admin_window.geometry()
admin_window.protocol("WM_DELETE_WINDOW", root.destroy)
admin_window.withdraw()



############################################## staff_window ##############################################
staff_window = Toplevel(root)
staff_window.title('صفحه کارمندان')
staff_window.config(bg=BG)
staff_window.resizable(False, False)
# staff_window.geometry()
staff_window.protocol("WM_DELETE_WINDOW", root.destroy)
staff_window.withdraw()


rf = RegistrationForm(connection, root, admin_window, staff_window)
rf.grid()
login_form = LoginForm(connection, root, admin_window, staff_window)
login_form.grid()
root.mainloop()