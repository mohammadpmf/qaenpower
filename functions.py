import hashlib


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

if __name__=='__main__':
    print(hash_password('a', '1'))
    word='salam'
    print(len(hash_password(word)), hash_password(word))
    p = input("Enter password: ")
    if hash_password(p)=='a893ce44036b095ec672bc890dea516ab89069f77fc9f02aadc0c9308761302ae7c3e25bbdcd7dafd7899d0186703eeb':
        print("Welcome")
