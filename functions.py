import hashlib
from datetime import datetime
import jdatetime
from Equation import Expression
import re


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


def round3(number:float) -> float|int:
    number = float(number)
    number = round(number, 3)
    if int(number)==number:
        return int(number)
    return number
    

# تابعی جهت بررسی این که نام یک متغیر مناسب است یا نه
def what_is_variable_name_problem(name: str, counters_variable_names: tuple):
    if name == "":
        return "نام متغیر را تعیین کنید"
    elif name in ['a', 'b']:
        return "برای نام متغیر نمی توانید از a و b استفاده کنید."
    elif not name.isidentifier():
        return "نام متغیر مناسب نیست"
    elif name in counters_variable_names:
        return "نام متغیر تکراری است و برای یکی از پارامترهای قبلی تعریف شده است."
    return None


# تابعی جهت بررسی این که فرمول نوشته شده درست است یا نه.
def what_is_formula_problem(formula: str, formula_parameters:str, counters_variable_names: tuple):
    parameters = formula_parameters.split()
    bad_params = [] # پارامترهایی که قبلا در دیتابیس ثبت نشده اند. اما کاربر به اشتباه به ما داده است.
    for p in parameters:
        if p not in counters_variable_names:
            bad_params.append(p)
    if bad_params:
        return f"پارامترهای زیر از قبل به عنوان هیچ متغیری ثبت نشده اند\n{bad_params}"
    try:
        fn = Expression(formula, parameters) # این خط به طور شگفت انگیزی خودش میاد متغیر پارامترز رو عوض میکنه. یعنی اگه لازم نشد من تغییری بدم و خودش با این که بقیه رو ننوشته بودم اضافه کرده. عجیبا غریبا :دی
        sample_values = []
        for i in parameters:
            sample_values.append(1)
        print(fn(*sample_values))
    except IndexError:
        return "در نحوه نوشتار فرمول، اشتباه تایپی وجود دارد"
    print(formula)
    sorted_parameters = parameters.copy()
    sorted_parameters.sort(key=len, reverse=True)
    print(sorted_parameters)
    print(formula)
    for p in sorted_parameters:
        formula=formula.replace(p, '1')
        print(formula)
    # try:
    _ = eval(formula)
    return None
    # except :
    #     return 'ss'

print(what_is_formula_problem('(a+b)*t+36*t+3+rrrt*a4+krt/krt2+ab', '', ('t', 'r', 'r2', 'a23', 'a', 'b', 'k')))

# if __name__=='__main__':
#     print(hash_password('admin', '1'))
#     word='salam'
#     print(len(hash_password(word)), hash_password(word))
#     p = input("Enter password: ")
#     if hash_password(p)=='a893ce44036b095ec672bc890dea516ab89069f77fc9f02aadc0c9308761302ae7c3e25bbdcd7dafd7899d0186703eeb':
#         print("Welcome")
