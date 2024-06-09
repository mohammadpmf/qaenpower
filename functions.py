import hashlib
from datetime import datetime
import jdatetime
from Equation import Expression
from ui_settings import PARAMETER_TYPES


def hash_password(password: str, salt="mohammad pourmohammadi fallah"):
    # salt = "mohammad pourmohammadi fallah"
    # اگه salt ثابت باشه، دو نفر که پسووررد یکسان بذارن، تو دیتابیس یه هش دارن و اگه پسورد یکی لو بره. اون یکی رو هم میشه فهمید.
    # برای این که این اتفاق نیفته، سالت رو به عنوان ورودی گرفتم و موقع ساختن آی دی طرف رو ارسال میکنم که یونیک هم باشه و هیچ ۲ تا 
    # پسوورد هش شده ای مثل هم نباشن. میشد بر اساس نام یا فامیلی هم نوشت. اما مشکلی که داره اینه که نام یا نام خانوادگی
    # دو نفر میتونه مثل هم باشه و پسوورد هم مثل هم بذارن. در این صورت باز هم به احتمال خیلی خیلی کمی قابل لو رفتن بود.
    # میشد ترکیبی کار کرد یا با یه چیز یونیک گذاشت. مثلا یوزرنیم. این طوری دیگه هیچ وقت مثل هم نمیشند. اما مشکل اینه که شاید
    # مدیر دیتابیس، یوزرنیم کسی رو عوض کنه. اگه هش رو از رو یوزرنیم میساختیم، وقتی عوض بشه پسوورد قبلی دیگه کار نمیکنه.
    # فکر کردم دیدم اگه یوزرنیم هم عوض بشه، آی دی دیگه عوض نمیشه و برای هر کسی هم یونیک هست. پس اگه آی دی رو به عنوان
    # سالت در نظر بگیرم، اگه دو نفر پسوورد یکسانی هم داشته باشن، مشخص نمیشه و اگه نام کاربری کسی هم عوض بشه یا نام
    # یا فامیلی، باز هم تغییری نمیکنه و پسووردش اعتبار داره. اگه آی دی عوض بشه که دیگه مدیر دیتابیس کرم داری :دی
    # نکته آخر این که برای این که تابع قبلی به مشکل نخوره، مقدار پیش فرض سالت رو همون محمد پورمحمدی فلاح گذاشتم.
    new_password = (password+salt).encode()
    # hashed_password = hashlib.md5(new_password)               # 32 raghame hex
    # hashed_password = hashlib.sha1(new_password)              # 40 raghame hex          
    # hashed_password = hashlib.sha224(new_password)            # 56 raghame hex   
    # hashed_password = hashlib.sha256(new_password)            # 64 raghame hex   
    hashed_password = hashlib.sha384(new_password)              # 96 raghame hex
    # hashed_password = hashlib.sha512(new_password)            # 128 raghame hex   
    # hashed_password = hashlib.sha3_224(new_password)          # 56 raghame hex   
    # hashed_password = hashlib.sha3_256(new_password)          # 64 raghame hex   
    # hashed_password = hashlib.sha3_384(new_password)          # 96 raghame hex   
    # hashed_password = hashlib.sha3_512(new_password)          # 128 raghame hex   
    # hashed_password = hashlib.shake_128(new_password)         # vaghti in ro estefade mikonim dakhele tabe e hexdigest ye voroodi behesh midim masalan 50 ba'd ta 100 ragham minevesht. neveshtam 2500 va ta 5000 ragham nevesht. ama bayad voroodi ro behesh bedim.
    # hashed_password = hashlib.shake_256(new_password)         # vaghti in ro estefade mikonim dakhele tabe e hexdigest ye voroodi behesh midim masalan 50 ba'd ta 100 ragham minevesht. neveshtam 2500 va ta 5000 ragham nevesht. ama bayad voroodi ro behesh bedim.
    hashed_password = hashed_password.hexdigest()
    return hashed_password


def get_jnow():
    '''
    get date_time of now in jalali format
    '''
    gnow = datetime.now()
    jnow = jdatetime.GregorianToJalali(gnow.year, gnow.month, gnow.day)
    jnow = jdatetime.datetime(jnow.jyear, jnow.jmonth, jnow.jday, gnow.hour, gnow.minute, gnow.second)
    return jnow


def round4(number:float) -> float|int:
    try:
        number = float(number)
    except ValueError:
        return 0
    number = round(number, 4)
    if int(number)==number:
        return int(number)
    return number
    

# تابعی جهت بررسی این که نام یک متغیر مناسب است یا نه
def what_is_variable_name_problem(name: str, counters_variable_names: tuple):
    if name == "":
        return "نام متغیر را تعیین کنید"
    elif name in ['a', 'b']:
        return "استفاده کنید a و b برای نام متغیر نمی توانید از"
    elif not name.isidentifier():
        return "نام متغیر مناسب نیست"
    elif name in counters_variable_names:
        return "نام متغیر تکراری است و برای یکی از پارامترهای قبلی تعریف شده است"
    return None

# تابعی که میشماره هر پارامتر چند جای دیگه تو فرمول ها استفاده شده که اگه حداقل یه بار استفاده شده بود، اجازه پاک کردن بهش ندیم
def how_many_times_parameters_variable_name_used_in_other_formulas(variable_name: str, formulas: list):
    count = 0
    for formula in formulas:
        parameters = []
        fn = Expression(formula, parameters)
        if variable_name in parameters:
            count+=1
    return count

# تابعی جهت بررسی این که فرمول نوشته شده درست است یا نه.
# در مرحله دوم که پارامترها رو خودم به دست میارم، دوباره برای همین تابع ارسال میکنم که بررسی کنه داخل دیتابیس هم باشن.
# در واقع دیگه لازم نیست دستی وارد بشه تو قسمت اول. اما به جای تابع جداگانه کلک زدم ۲ بار همین تابع رو صدا کردم.
def what_is_formula_problem(formula: str, formula_parameters:list, variable_name: str, counters_variable_names: tuple, type: str):
    parameters = formula_parameters
    if variable_name in parameters:
        return "از نام متغیر پارامتر نمی توان در فرمول خودش استفاده کرد"
    bad_params = [] # پارامترهایی که قبلا در دیتابیس ثبت نشده اند. اما کاربر به اشتباه به ما داده است.
    if type==PARAMETER_TYPES[2]:
        for p in parameters:
            if p =='b':
                return f"استفاده کرد b در فرمول پارامترهای محاسباتی نمیتوان از"
    for p in parameters:
        if p in ['a', 'b']:
            continue
        if p not in counters_variable_names:
            bad_params.append(p)
    if bad_params:
        return f"پارامترهای زیر از قبل به عنوان نام هیچ متغیری ثبت نشده اند\n{bad_params}"
    try:
        parameters.clear()
        fn = Expression(formula, parameters) # این خط به طور شگفت انگیزی خودش میاد متغیر پارامترز رو عوض میکنه. یعنی لازم نشد من تغییری بدم و خودش با این که بقیه رو ننوشته بودم اضافه کرده. عجیبا غریبا :دی
        # کدهاش رو نگاه کردم گمج ها ورودی دوم رو یه لیست تعریف کردن که مقدار پیش فرضش یه لیست خالی هست.
        # وقتی من هم لیست میدم لیست من رو برمیداره و کارها رو رو اون اعمال میکنه. یه کپی ازش نگرفتن 🤦‍♂️
        # به خاطر همین خودش لیست من رو تغییر میده که البته اینجا به نفع من شد 😁
        sample_values = []
        for i in parameters:
            sample_values.append(1)
        fn(*sample_values) # اگه این خط با موفقیت انجام بشه، یعنی از نظر کلاس اکسپرشن مشکلی نداره و به علاوه و منها اینا درست جاگذاری شده. اما حروفی که کنار هم نوشته شدن رو به عنوان یه متغیر در نظر میگیره که شاید واقعا نباشن و اشتباه باشه. پس با ایول هم خودم تست کردم.
    except IndexError:
        return "در نحوه نوشتار فرمول، اشتباه تایپی وجود دارد"
    # توضیح کدهای زیر بعد از این خطوط
    sorted_parameters = parameters.copy()
    sorted_parameters.sort(key=len, reverse=True)
    for p in sorted_parameters:
        formula=formula.replace(p, '1')
    # اگه اسم متغیر t داخل فرمول بود و همچنین متغیرهای t22 و ttrt و غیره
    # این باعث میشد که اولی خرابکاری کنه و موقعی که ریپلیس رو صدا کردم به هم بریزه.
    # برای این که این اتفاق نیفته گفتم اول بیاد اونها رو به ترتیب طول از بزرگ به کوچیک مرتب کنه
    # بعد از بزرگ ریپلیس کنه یعنی اول مثلا ttrt رو جایگزین کنه که بعدا وقتی خواست 
    # t رو جایگزین کنه، روی این یا بقیه که با تی شروع میشن مشکلی نداشته باشه.
    # برای این که ترتیب لیست پارامترهای اصلی مشکل نخوره، یه کپی از لیست گرفتم و اون رو مرتب کردم.
    # اما اصلی سر جاش هست.
    try:
        eval(formula) # تا اینجا خدا رو شکر مشکل نداشت. اما ترای و. اکسپت رو برداشتم که اگه اروری خورد بفهمم و بعدا ریترنش کنم.
        return parameters
    except TypeError:
        return 'در نوشتن فرمول دقت کنید'
    except SyntaxError:
        return 'در نوشتن فرمول دقت کنید'
    except NameError:
        return 'در نوشتن فرمول دقت کنید'
    except:
        return 'باز هم در نوشتن فرمول دقت کنید'

# تابعی که پارامتر ها رو از تو فرمول در بیاره که مقادیرشون رو از تو دیتابیس بخوونیم.
def get_formula_parameters(formula: str) -> list:
    parameters = []
    Expression(formula, parameters)
    return parameters

# تابعی که در برنامه مقدار پارامتر مورد نظر را حساب کند و نمایش دهد.
def calculate_fn(formula: str, parameters: list, values: list):
    '''
    مقدار محاسبه را با دقت چهار رقم اعشار تحویل میدهد
    در صورتی که به مشکل بخورد ۰ تحویل می دهد
    '''
    fn = Expression(formula, parameters)
    try:
        answer = round4(fn(*values))
        return answer
    except TypeError:
        print("Warning in calculate_fn except layer 1 :D (Decimal & Float)")
        values_copy = []
        for item in values:
            values_copy.append(float(item))
        try:
            answer = round4(fn(*values_copy))
            return answer
        except TypeError:
            print("Error in calculate_fn except layer 2 :D (Decimal & Float)")
            return 0
    except ZeroDivisionError:
        print("Warning in calculate_fn except layer 1 :D (Zero Division)")
        return 0
    
if __name__=='__main__':
    print(hash_password('admin', '1'))
    word='salam'
    print(len(hash_password(word)), hash_password(word))
    p = input("Enter password: ")
    if hash_password(p)=='a893ce44036b095ec672bc890dea516ab89069f77fc9f02aadc0c9308761302ae7c3e25bbdcd7dafd7899d0186703eeb':
        print("Welcome")
