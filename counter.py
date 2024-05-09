from ui_settings import *
from PIL import Image, ImageTk
from authentication import COUNTER_TYPES, DEFAULT_VALUES
from models import Counter
from functions import round3
from connection import Connection


class CounterWidget(Counter):
    def __init__(self, connection: Connection, root: Tk, part, place, name, variable_name, previous_value=0, current_value=0, formula='', type='کنتور', default_value=0, unit=None, warning_lower_bound=None, warning_upper_bound=None, alarm_lower_bound=None, alarm_upper_bound=None, id=None, place_title=None, *args, **kwargs):
        super().__init__(part, place, name, variable_name, previous_value, current_value, formula, type, default_value, unit, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, id, place_title)
        self.connection = connection
        self.root = root
        self.frame = LabelFrame(self.root, text=f"کنتور {self.name}", cnf=CNF_LBL_FRM, padx=16, pady=8, labelanchor='n', bg=BG, *args, **kwargs)
        if self.type==COUNTER_TYPES[0]:
            self.img = Image.open('copy-icon.png')
            self.img = self.img.resize((20, 20))
            self.img = ImageTk.PhotoImage(self.img)
            self.btn_copy = Button(self.frame, image=self.img, cnf=CNF_BTN2, command=self.copy_down, *args, **kwargs)
            self.entry_current_counter = Entry(self.frame, cnf=CNF_ENTRY2, *args, **kwargs)
            if self.default_value==DEFAULT_VALUES[0]:
                self.entry_current_counter.insert(0, round3(self.previous_value))
            elif self.default_value==DEFAULT_VALUES[1]:
                self.entry_current_counter.insert(0, DEFAULT_VALUES[1])
            elif self.default_value==DEFAULT_VALUES[2]:
                self.entry_current_counter.delete(0, END)
            self.entry_previous_counter = Label(self.frame, cnf=CNF_LBL2, text=round3(self.previous_value), *args, **kwargs)
            self.entry_workout = Entry(self.frame, cnf=CNF_ENTRY2, *args, **kwargs)
            self.entry_workout.insert(0, 'کارکرد')
            self.entry_workout.config(state='readonly')
            self.boolean_var_bad = BooleanVar(self.frame)
            self.checkbutton_bad = Checkbutton(self.frame, cnf=CNF_CHB2, variable=self.boolean_var_bad, text='خرابی کنتور', command=self.check, *args, **kwargs)
            self.entry_workout.bind('<Return>', self.confirm)
            self.entry_workout.bind('<KeyRelease>', self.check_color)
            self.entries = [self.entry_previous_counter, self.entry_current_counter, self.entry_workout] # میخواستم برای دیسبل کردن و اینیبل کردن یه حلقه بزنم. همه شون رو ریختم تو یه لیست داخل آبجکت که تو تابع چک کارم راحت تر بشه.

            self.btn_copy.grid(row=1, column=3, cnf=CNF_GRID2)
            self.entry_workout.grid(row=2, column=1, cnf=CNF_GRID2)
            self.entry_current_counter.grid(row=2, column=2, columnspan=2, cnf=CNF_GRID2)
            self.checkbutton_bad.grid(row=3, column=1, cnf=CNF_GRID2)
            self.entry_previous_counter.grid(row=3, column=2, columnspan=2, cnf=CNF_GRID2, sticky='ew')

        elif self.type==COUNTER_TYPES[1]:
            self.entry_current_counter = Entry(self.frame, cnf=CNF_ENTRY2, *args, **kwargs)
            if self.default_value==DEFAULT_VALUES[0]:
                self.entry_current_counter.insert(0, round3(self.previous_value))
            elif self.default_value==DEFAULT_VALUES[1]:
                self.entry_current_counter.insert(0, DEFAULT_VALUES[1])
            elif self.default_value==DEFAULT_VALUES[2]:
                self.entry_current_counter.delete(0, END)
            self.entry_current_counter.grid(row=1, column=1, cnf=CNF_GRID2)
        elif self.type==COUNTER_TYPES[2]:
            self.entry_current_counter = Label(self.frame, text='در حال محاسبه', cnf=CNF_LBL2, *args, **kwargs)
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
            msb.showinfo("پیام موفقیت", f"مقدار {value} با موفقیت برای کنتور {self.name} از مکان {self.place_title} ثبت شد.")
        else:
            msb.showerror("ارور", result_message)

    def update_workout(self, event=None):
        if self.type==COUNTER_TYPES[0] and (event.keysym in '0123456789' or event.keysym=='period'):
            try:
                workout = float(self.entry_current_counter.get()) - float(self.entry_previous_counter['text']) # میشه از دیتابیس گرفت که دقیق تر باشه. اما من نگرفتم و از رو همون ۳ رقم اعشار خووندم.
                workout = round3(workout)
                self.entry_workout.config(state='normal')
                self.entry_workout.delete(0, END)
                self.entry_workout.insert(0, workout)
                self.entry_workout.config(state='readonly')
                self.check_color()
            except:
                return

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
            self.frame.config(bg=bg)
        except:
            pass

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)

    def place(self, *args, **kwargs):
        self.frame.place(*args, **kwargs)


if __name__ == "__main__":
    root = Tk()
    root.geometry('1000x800')
    root.title('ثبت کنتور')
    c1 = CounterWidget('', root, 1, 1, name=2, variable_name=1).grid(row=2, column=1)
    c2 = CounterWidget('', root, 1, 1, name=3, variable_name=1).grid(row=3, column=1)
    c3 = CounterWidget('', root, 1, 1, type='محاسباتی', name=4, variable_name=1).grid(row=4, column=1)
    c4 = CounterWidget('', root, 1, 1, type='ثابت', name=50, variable_name=1).grid(row=4, column=2)
    root.mainloop()