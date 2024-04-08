from tkinter import *
from tkinter import ttk
import jdatetime

FONT = ('B Nazanin', 24)
CNF_GRID={
    'padx': 5,
    'pady': 3,
}
month_names = {
    1: 'فروردین',
    2: 'اردیبهشت',
    3: 'خرداد',
    4: 'تیر',
    5: 'مرداد',
    6: 'شهریور',
    7: 'مهر',
    8: 'آبان',
    9: 'آذر',
    10: 'دی',
    11: 'بهمن',
    12: 'اسفند',
}
weekdays = {
    0: 'شنبه',
    1: 'یکشنبه',
    2: 'دوشنبه',
    3: 'سه شنبه',
    4: 'چهارشنبه',
    5: 'پنجشنبه',
    6: 'جمعه',
}

class DatePicker:
    days_list = [i for i in range(1, 32)]
    months_list = [i for i in range(1, 13)]
    years_list = [i for i in range(1400, 1410)]
   
    def __init__(self, root:Toplevel):
        self.root = root
        self.frame = Frame(self.root)
        self.year = StringVar(self.frame)
        self.month = StringVar(self.frame)
        self.day = StringVar(self.frame)
        self.year.set('سال')
        self.month.set('ماه')
        self.day.set('روز')
        self.combo_year = ttk.Combobox(self.frame, values=self.years_list, textvariable=self.year, width=7, state='readonly', font=FONT, justify='center')
        self.combo_month = ttk.Combobox(self.frame, values=self.months_list, textvariable=self.month, width=5, state='readonly', font=FONT, justify='center')
        self.combo_day = ttk.Combobox(self.frame, values=self.days_list, textvariable=self.day, width=5, state='readonly', font=FONT, justify='center')
        self.combo_year.bind("<<ComboboxSelected>>", self.check_date)
        self.combo_month.bind("<<ComboboxSelected>>", self.check_date)
        self.combo_day.bind("<<ComboboxSelected>>", self.check_date)
        self.label_date = Label(self.frame, text="!!! تاریخ نامعتبر !!!", font=FONT)
        self.combo_year.grid(row=1, column=1, cnf=CNF_GRID)
        self.combo_month.grid(row=1, column=2, cnf=CNF_GRID)
        self.combo_day.grid(row=1, column=3, cnf=CNF_GRID)
        self.label_date.grid(row=2, column=1, columnspan=3, cnf=CNF_GRID)
    
    def check_date(self, event=None):
        y = self.year.get()
        m = self.month.get()
        d = self.day.get()
        try:
            if y=='سال' or m=='ماه' or d=='روز':
                return
            else:
                date = jdatetime.date(int(y), int(m), int(d))
                temp = f"{'تاریخ':10} {weekdays.get(date.weekday())} {d} {month_names.get(int(m))} {y}"
                self.label_date.config(text=temp)
        except ValueError:
            temp = "!!! تاریخ نامعتبر !!!"
            self.label_date.config(text=temp)

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

if __name__ == '__main__':
    root = Tk()
    dp = DatePicker(root)
    dp.grid(row=1, column=1)
    root.mainloop()