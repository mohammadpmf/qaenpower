from authentication import *
from test_scroll import Part
from my_datetime import DatePicker

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
root.withdraw()
create_my_theme() # اول تو ستینگز بود. اما چون پنجره ای ساخته نشده بود یکی جدید میساخت. به خاطر همین تبدیلش کردم به تابع و اونجا نوشتم اما اینجا صداش کردم.



############################################## admin_window ##############################################
admin_window = Toplevel(root)
admin_window.title('صفحه مدیریت')
admin_window.config(bg=BG)
admin_window.resizable(False, False)
admin_window.geometry(f"+{s_width//4}+0")
admin_window.protocol("WM_DELETE_WINDOW", root.destroy)
# admin_window.withdraw()



############################################## staff_window ##############################################
staff_window = Toplevel(root)
staff_window.title('صفحه کارمندان')
staff_window.config(bg=BG)
# staff_window.resizable(False, False)
# staff_window.geometry()
# staff_window.geometry(f"{WIDTH}x{HEIGHT}")
staff_window.protocol("WM_DELETE_WINDOW", root.destroy)
# staff_window.withdraw()
tab_bar_staff_window = ttk.Notebook(staff_window)
tab_bar_staff_window.place(x=200, y=40, width=1000, height=800)
tab_bar_staff_window.pack(expand=True, fill='both')
staff_window.focus_force()
tabs_list = []
parts_tab = []
places_with_counters = []
parts=connection.get_all_parts()
for i, part in enumerate(parts):
    places_with_counters.clear()
    tabs_list.append(ttk.Frame(tab_bar_staff_window))
    # date_picker = DatePicker(tab_bar_staff_window)
    # date_picker.pack()
    tabs_list[i].pack()
    tab_bar_staff_window.add(tabs_list[i], text =f'بخش {part[1]}')
    temp_places=connection.get_all_places_by_part_id(part[0])
    for place in temp_places:
        counters = connection.get_all_counters_of_this_part_and_place(part_id=place[2], place_id=place[0])
        places_with_counters.append(counters)
    parts_tab.append(Part(connection, tabs_list[i], places_with_counters))
    # parts[i].grid(row=1, column=1)
    parts_tab[i].pack()
    # parts[i].place(width=1024, height=400)
tab_bar_staff_window.pack(expand = 1, fill ="both")

rf = RegistrationForm(connection, root, admin_window, staff_window)
rf.grid()
login_form = LoginForm(connection, root, admin_window, staff_window)
login_form.grid()
root.mainloop()