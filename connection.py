import pymysql
from models import Staff, Counter
from functions import hash_password
from my_datetime import get_jnow

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
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`parts` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `title` VARCHAR(45) NOT NULL, `order` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `order_UNIQUE` (`order` ASC) VISIBLE);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`places` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `title` VARCHAR(45) NOT NULL, `part` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE, INDEX `part_idx` (`part` ASC) VISIBLE, UNIQUE INDEX `place_part` (`title` ASC, `part` ASC) INVISIBLE, CONSTRAINT `part` FOREIGN KEY (`part`) REFERENCES `qaenpower`.`parts` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`counters` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `name` VARCHAR(45) NOT NULL, `type` VARCHAR(45) NOT NULL, `unit` VARCHAR(45) NULL, `default_value` VARCHAR(45) NOT NULL, `variable_name` VARCHAR(45) NOT NULL, `warning_lower_bound` DECIMAL(20,10) UNSIGNED NULL, `warning_upper_bound` DECIMAL(20,10) UNSIGNED NULL, `alarm_lower_bound` DECIMAL(20,10) UNSIGNED NULL, `alarm_upper_bound` DECIMAL(20,10) UNSIGNED NULL, `formula` VARCHAR(255) NOT NULL DEFAULT '', `part` INT UNSIGNED NOT NULL, `place` INT UNSIGNED NOT NULL, `previous_value` DECIMAL(20,10) UNSIGNED NOT NULL DEFAULT 0, `current_value` DECIMAL(20,10) UNSIGNED NOT NULL DEFAULT 0, PRIMARY KEY (`id`), UNIQUE INDEX `variable_name_UNIQUE` (`variable_name` ASC) VISIBLE, UNIQUE INDEX `counter_place_part` (`name` ASC, `place` ASC, `part` ASC) VISIBLE, INDEX `part2_idx` (`part` ASC) VISIBLE, INDEX `place_idx` (`place` ASC) VISIBLE, CONSTRAINT `part2` FOREIGN KEY (`part`) REFERENCES `qaenpower`.`parts` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT, CONSTRAINT `place` FOREIGN KEY (`place`) REFERENCES `qaenpower`.`places` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`counters_log` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `value` DECIMAL(20,10) UNSIGNED NOT NULL, `date_time` DATETIME NOT NULL, `counter` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), CONSTRAINT `counter` FOREIGN KEY (`counter`) REFERENCES `qaenpower`.`counters` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE);"
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
            id=result[0]
            return self.update_users_password(id, password)
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
    
    def update_users_password(self, id, password):
        salt = str(id)
        password = hash_password(password, salt)
        query = "UPDATE `qaenpower`.`users` SET `password` = %s WHERE (`id` = %s);"
        values = (password, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def login(self, username, password):
        query = "SELECT `name`, `surname`, `username`, `password`, `access_level`, `wrong_times`, `id` FROM `qaenpower`.`users` where username=%s;"
        values = (username, )
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result in [None, '', ()]:
            return ("نام کاربری یافت نشد", -1)
        p = Staff(*result)
        if p.wrong_times>=10:
            return ("نام کاربری شما مسدود شده است. به مدیر دیتابیس مراجعه نمایید", -3)
        salt = str(p.id)
        password = hash_password(password, salt)
        if p.password==password:
            p.wrong_times=0
            self.update_wrong_times(p.id, 0)
            return ('ok', p)
        else:
            p.wrong_times+=1
            self.update_wrong_times(p.id, p.wrong_times)
            return (f"رمز عبور اشتباه است. دقت کنید که نمیتوانید بیش از {WRONG_LIMIT} بار پشت سر هم رمز عبور خود را اشتباه وارد کنید. تعداد فرصت های باقیمانده: {WRONG_LIMIT-p.wrong_times}", -2)
        
    def update_wrong_times(self, id, wrong_times):
        query = "UPDATE `qaenpower`.`users` SET `wrong_times` = %s WHERE (`id` = %s);"
        values = wrong_times, id
        self.cursor.execute(query, values)
        self.connection.commit()

    def create_part(self, title):
        query = "INSERT INTO `qaenpower`.`parts` (`title`, `order`) VALUES (%s, 0);"
        values = (title, )
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT * FROM `qaenpower`.`parts` where title=%s;"
            values = (title, )
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            if result in [None, '', ()]:
                return ("بخش یافت نشد", -1)
            id=result[0]
            return self.update_part_sort(id, id)
        except pymysql.err.IntegrityError as error:
            return (f"بخش {title} قبلا ثبت شده است", error)
    
    def update_part_sort(self, id, order):
        query = "UPDATE `qaenpower`.`parts` SET `order` = %s WHERE (`id` = %s);"
        values = (order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def create_place(self, title, part_id):
        query = "INSERT INTO `qaenpower`.`places` (`title`, `part`) VALUES (%s, %s);"
        values = title, part_id
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            part_id, part_name = self.get_part_by_id(part_id)
            return (f"مکان {title} برای بخش {part_name} قبلا ثبت شده است", error)

    def get_part_by_id(self, id):
        query = "SELECT * FROM `qaenpower`.`parts` WHERE id=%s;"
        values = (id, )
        self.cursor.execute(query, values)
        return self.cursor.fetchone()
  
    def create_counter(self, name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place):
        query = "INSERT INTO `qaenpower`.`counters` (`name`, `type`, `unit`, `default_value`, `variable_name`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `formula`, `part`, `place`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        part_id, part_name = self.get_part_by_title(part)
        place_id, place_name, place_part_id = self.get_place_by_title_and_part_id(place, part_id)
        values = name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part_id, place_id
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            temp = str(error)
            if 'counters.variable_name_UNIQUE' in temp:
                return ("نام متغیر تکراری است", 2)
            elif 'counters.counter_place_part' in temp:
                return ("در این بخش و مکان، کنتوری با این نام قبلا ثبت شده است", 2)
   
    def get_part_by_title(self, title):
        query = "SELECT * FROM `qaenpower`.`parts` WHERE title=%s;"
        self.cursor.execute(query, title)
        return self.cursor.fetchone()
 
    def get_place_by_title_and_part_id(self, title, part_id):
        query = "SELECT * FROM `qaenpower`.`places` WHERE title=%s AND part=%s;"
        values = title, part_id
        self.cursor.execute(query, values)
        return self.cursor.fetchone()

    def get_all_parts(self):
        query = "SELECT * FROM `qaenpower`.`parts`;"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_all_places_by_part_id(self, part_id):
        query = "SELECT * FROM `qaenpower`.`places` WHERE `part`=%s;"
        self.cursor.execute(query, part_id)
        return self.cursor.fetchall()
    
    def get_all_counters_of_this_part_and_place(self, part_id, place_id):
        query = "SELECT `qaenpower`.`counters`.`part`, `place`, `name`, `variable_name`, `previous_value`, `current_value`, `formula`, `type`, `default_value`, `unit`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `qaenpower`.`counters`.`id`, `title` FROM `qaenpower`.`counters` join `qaenpower`.`places` ON (`qaenpower`.`counters`.`place`=`qaenpower`.`places`.`id`) WHERE `qaenpower`.`counters`.`part`=%s AND `place`=%s;"
        values = part_id, place_id
        self.cursor.execute(query, values)
        counters = []
        for counter in self.cursor.fetchall():
            t = Counter(*counter)
            counters.append(t)
        return counters

    def get_place_name_by_id_and_part_id(self, title, part_id):
        query = "SELECT * FROM `qaenpower`.`places` WHERE title=%s AND part=%s;"
        values = title, part_id
        self.cursor.execute(query, values)
        return self.cursor.fetchone()

    def create_counter_log(self, value, counter_id):
        query = "INSERT INTO `qaenpower`.`counters_log` (`value`, `date_time`, `counter`) VALUES (%s, %s, %s);"
        values = value, get_jnow(), counter_id
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def update_counter_usage(self, value, counter_id):
        query = "SELECT `previous_value`, `current_value` FROM `qaenpower`.`counters` where `id` = %s;"
        values = (counter_id, )
        self.cursor.execute(query, values)
        a, b = self.cursor.fetchone()
        query = "UPDATE `qaenpower`.`counters` SET `previous_value` = %s, `current_value` = %s WHERE (`id` = %s);"
        values = (b, value, counter_id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def get_all_counters_variable_names(self):
        query = "SELECT variable_name FROM `qaenpower`.`counters`;"
        self.cursor.execute(query)
        names = []
        for item in self.cursor.fetchall():
            names.append(item[0])
        return tuple(names)

    def get_current_value_of_counter_by_variable_name(self, variable_name):
        query = "SELECT current_value FROM `qaenpower`.`counters` WHERE variable_name=%s;"
        values = (variable_name, )
        self.cursor.execute(query, values)
        return self.cursor.fetchone()[0]

if __name__ == "__main__":
    c = Connection()
