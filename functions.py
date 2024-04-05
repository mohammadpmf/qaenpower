import hashlib


def hash_password(password: str):
    salt = "mohammad pourmohammadi fallah"
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
    word='salam'
    print(len(hash_password(word)), hash_password(word))
    p = input("Enter password: ")
    if hash_password(p)=='a893ce44036b095ec672bc890dea516ab89069f77fc9f02aadc0c9308761302ae7c3e25bbdcd7dafd7899d0186703eeb':
        print("Welcome")
