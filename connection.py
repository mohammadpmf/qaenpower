import pymysql
from models import Staff as Person
from functions import hash_password

WRONG_LIMIT=10

class Connection():
    def __init__(self, host='127.0.0.1', user='root', password='root'):
        self.host = host
        self.user = user
        self.password = password
        self.connection = pymysql.connect(host=self.host, user=self.user, passwd=self.password, charset='utf8')
        self.cursor = self.connection.cursor()
        query = "CREATE SCHEMA IF NOT EXISTS `qaenpower`;"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`users` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `name` VARCHAR(64) NOT NULL, `surname` VARCHAR(64) NOT NULL, `username` VARCHAR(64) NOT NULL, `password` VARCHAR(128) NOT NULL, `access_level` TINYINT(1) NOT NULL DEFAULT 2, `wrong_times` TINYINT(2) NOT NULL DEFAULT 0, PRIMARY KEY (`id`),UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`parts` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `title` VARCHAR(45) NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE, UNIQUE INDEX `title_UNIQUE` (`title` ASC) VISIBLE);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`places` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `title` VARCHAR(45) NOT NULL, `part` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE, INDEX `part_idx` (`part` ASC) VISIBLE, UNIQUE INDEX `place_part` (`title` ASC, `part` ASC) INVISIBLE, CONSTRAINT `part` FOREIGN KEY (`part`) REFERENCES `qaenpower`.`parts` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`counters` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `name` VARCHAR(45) NOT NULL, `type_` VARCHAR(45) NOT NULL, `unit` VARCHAR(45) NULL, `default_value` VARCHAR(45) NOT NULL, `variable_name` VARCHAR(45) NOT NULL, `warning_lower_bound` DECIMAL(20,10) NULL, `warning_upper_bound` DECIMAL(20,10) NULL, `alarm_lower_bound` DECIMAL(20,10) NULL, `alarm_upper_bound` DECIMAL(20,10) NULL, `formula` VARCHAR(255) NOT NULL, `part` INT UNSIGNED NOT NULL, `place` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE, UNIQUE INDEX `variable_name_UNIQUE` (`variable_name` ASC) INVISIBLE, INDEX `part2_idx` (`part` ASC) VISIBLE, INDEX `place_idx` (`place` ASC) VISIBLE, CONSTRAINT `part2` FOREIGN KEY (`part`) REFERENCES `qaenpower`.`parts` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT, CONSTRAINT `place` FOREIGN KEY (`place`) REFERENCES `qaenpower`.`places` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT);"
        self.cursor.execute(query)


    def create_user(self, name, surname, username, password):
        query = "INSERT INTO `qaenpower`.`users` (`name`, `surname`, `username`, `password`) VALUES (%s, %s, %s, %s);"
        values = name, surname, username, password # چون میخوایم پسوورد رو همین الان عوض کنیم دیگه دفعه اول الکی هشش نمیکنیم.
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT * FROM `qaenpower`.`users` where username=%s;"
            values = (username, )
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            if result in [None, '', ()]:
                return ("نام کاربری یافت نشد", -1)
            _id=result[0]
            return self.update_users_password(_id, password)
        except pymysql.err.IntegrityError as error:
            return (f"نام کاربری {username} قبلا ثبت شده است", error)
        except pymysql.err.DataError as error:
            temp = str(error)
            if 'surname' in temp:
                temp='نام خانوادگی'
            elif 'username' in temp:
                temp='نام کاربری'
            elif 'name' in temp: # اول این رو به عنوان اولی گذاشتم. اما همه همین ارور رو میدادن. چون توی سرنیم و یوزرنیم هم کلمه نیم به کار رفته :دی. جالب بود گفتم بنویسم.
                temp='نام'
            return (f"طول فیلد {temp} بیش از اندازه تعیین شده است", error)

    def login(self, username, password):
        query = "SELECT * FROM `qaenpower`.`users` where username=%s;"
        values = (username, )
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result in [None, '', ()]:
            return ("نام کاربری یافت نشد", -1)
        # p = Person(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
        # اول این طوری نوشته بودم. بعد برای بهتر کردن کدها این شکلیش کردم با کلی تحقیق :)
        p = Person(*result)
        if p.wrong_times>=10:
            return ("نام کاربری شما مسدود شده است. به مدیر دیتابیس مراجعه نمایید", -3)
        salt = str(p._id)
        password = hash_password(password, salt)
        if p.password==password:
            p.wrong_times=0
            self.update_wrong_times(p._id, 0)
            return ('ok', p)
        else:
            p.wrong_times+=1
            self.update_wrong_times(p._id, p.wrong_times)
            return (f"رمز عبور اشتباه است. دقت کنید که نمیتوانید بیش از {WRONG_LIMIT} بار پشت سر هم رمز عبور خود را اشتباه وارد کنید. تعداد فرصت های باقیمانده: {WRONG_LIMIT-p.wrong_times}", -2)
        
    def update_wrong_times(self, _id, wrong_times):
        query = "UPDATE `qaenpower`.`users` SET `wrong_times` = %s WHERE (`id` = %s);"
        values = wrong_times, _id
        self.cursor.execute(query, values)
        self.connection.commit()

    def update_users_password(self, _id, password):
        salt = str(_id)
        password = hash_password(password, salt)
        query = "UPDATE `qaenpower`.`users` SET `password` = %s WHERE (`id` = %s);"
        values = (password, _id)
        
        # try except
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)
        

    def create_counter(self):
#         query = "INSERT INTO `qaenpower`.`counters` \
# (`name`, `type_`, `unit`, `default_value`, `variable_name`, `warning_lower_bound`, `warning_upper_bound`,\
#  `alarm_lower_bound`, `alarm_upper_bound`, `formula`, `part`, `place`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
#         values = name, type_, unit, default_value, variable_name, warning_lower_bound

        pass

    def update_counter(self):
        pass

    def create_part(self, title):
        query = "INSERT INTO `qaenpower`.`parts` (`title`) VALUES (%s);"
        try:
            self.cursor.execute(query, title)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            return (f"بخش {title} قبلا ثبت شده است", error)

    def create_place(self, title, part):
        query = "INSERT INTO `qaenpower`.`places` (`title`, `part`) VALUES (%s, %s);"
        values = title, part
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            part_id, part_name = self.get_part_by_id(part)
            return (f"مکان {title} برای بخش {part_name} قبلا ثبت شده است", error)
        
    def get_part_by_id(self, id_):
        query = "SELECT * FROM `qaenpower`.`parts` WHERE id=%s;"
        self.cursor.execute(query, id_)
        return self.cursor.fetchone()

    def get_part_by_title(self, title):
        query = "SELECT * FROM `qaenpower`.`parts` WHERE title=%s;"
        self.cursor.execute(query, title)
        return self.cursor.fetchone()
        
    def get_all_parts(self):
        query = "SELECT * FROM `qaenpower`.`parts`;"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_all_places_by_part_id(self, part_id):
        query = "SELECT * FROM `qaenpower`.`places` WHERE `part`=%s;"
        self.cursor.execute(query, part_id)
        return self.cursor.fetchall()

if __name__ == "__main__":
    c = Connection()
