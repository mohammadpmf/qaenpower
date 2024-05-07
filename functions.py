import hashlib
from Equation import Expression
import re
# from connection import Connection

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


def round3(number:float) -> float|int:
    number = float(number)
    number = round(number, 3)
    if int(number)==number:
        return int(number)
    return number
    

def what_is_variable_name_problem(name: str, counters_variable_names: tuple):
    if name == "":
        return "نام متغیر را تعیین کنید"
    elif name in ['a', 'b']:
        return "برای نام متغیر نمی توانید از a و b استفاده کنید."
    elif not name.isidentifier():
        return "نام متغیر مناسب نیست"
    elif name in counters_variable_names:
        return "نام متغیر تکراری است و برای یکی از کنتورهای قبلی تعریف شده است."
    return None


def what_is_formula_problem(formula: str, formula_parameters:str, counters_variable_names: tuple, connection):
    parameters = formula_parameters.split()
    bad_params = [] # پارامترهایی که قبلا در دیتابیس ثبت نشده اند. اما کاربر به اشتباه به ما داده است.
    for p in parameters:
        if p not in counters_variable_names:
            bad_params.append(p)
    if bad_params:
        return f"پارامترهای زیر به عنوان متغیر هیچ کنتوری ثبت نشده اند\n{bad_params}"
    # اگه تا اینجا مشکلی نبود، همه متغیرها درستند. فقط ممکنه نحوه نوشتن اشتباه باشه. بهش میگم که 
    # به جای همه متغیر ها ۱ بذاره که ببینم میشه مقدار فرمول رو حساب کرد یا نه. ممکنه توش ۲۰ تا 
    # + گذاشته بشه که خب مشکل داره. یا مثلا ۲ تا اسلش هم مشکل داره.
    for p in parameters:
        # temp = connection.get_current_value_of_counter_by_variable_name(p)
        # formula = formula.replace(p, str(float(temp)))
        formula = formula.replace(p, '1')
    formula = formula.replace('a', '1')
    formula = formula.replace('b', '1')
    formula = formula.replace('//', '///') # ایول به ۲ تا اسلش گیر نمیده. ولی اکسپرشن بهش گیر میداد. به خاطر همین من گفتم اگه ۲ تا اسلش بود ۳ تاش بکنه که ایول هم بهش گیر بده
    try:
        eval(formula)
        return None
    except SyntaxError:
        return "در نحوه نوشتار فرمول اشتباهی رخ داده است"
    except NameError:
        return "متغیرهای فرمولبه درستی در قسمت مربوطه ذکر نشده اند"
    # if re.search(r'\ba\b', formula):
    #     temp = connection.get_current_value_of_counter_by_variable_name(p)
    #     print(i)
    # for i in formula:
    #     "rrr+2*a-3*(term5+b)"
    #     t2 + a222 +(b-a)
    #     if re.search(r'\ba\b', formula):
    #     print(i)
    # fn = Expression("3*t+4*(t2-6)+8",("t", "t2"))
    # print(fn(3,4))
# connection = Connection()
# print(what_is_formula_problem("a23+a23+a23+a27+abc+b/a", 'a23 a27 abc', ('a23', 'a27', 'abc', 'adfasf', 'at56', 'class', 'def', 'garm', 'gas', 'r56', 'r567', 'rr_ewr', 'rr_ewr4', 'rrr', 's_4345', 't2', 'term', 'tr9', 'yyt'), connection))


if __name__=='__main__':
    print(hash_password('admin', '1'))
    word='salam'
    print(len(hash_password(word)), hash_password(word))
    p = input("Enter password: ")
    if hash_password(p)=='a893ce44036b095ec672bc890dea516ab89069f77fc9f02aadc0c9308761302ae7c3e25bbdcd7dafd7899d0186703eeb':
        print("Welcome")
