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
treev = ttk.Treeview(root, selectmode ='browse')
treev.grid(row=1, rowspan=10, column=1, columnspan=10, sticky='news')
verscrlbar = ttk.Scrollbar(root, orient ="vertical", command = treev.yview)
verscrlbar.grid(row=1, rowspan=10, column=11, columnspan=10, sticky='news')
treev.configure(yscrollcommand = verscrlbar.set)
treev["columns"] = ("1")
treev['show'] = 'headings'
treev.column("1", width = 90, anchor ='c')
treev.heading("1", text ="نام بخش")
treev.insert("", 'end', text ="L1", values =("Nidhi"))
treev.insert("", 'end', text ="L2",values =("Nisha"))
treev.insert("", 'end', text ="L3",values =("Preeti"))
treev.insert("", 'end', text ="L4",values =("Rahul"))
treev.insert("", 'end', text ="L5", values =("Sonu"))
treev.insert("", 'end', text ="L6",values =("Rohit"))
treev.insert("", 'end', text ="L7", values =("Geeta"))
treev.insert("", 'end', text ="L8", values =("Ankit"))
treev.insert("", 'end', text ="L10", values =("Mukul"))
rf = RegistrationForm(connection, root, admin_window, staff_window)
rf.grid()
login_form = LoginForm(connection, root, admin_window, staff_window)
login_form.grid()
root.mainloop()