import pymysql
from models import CounterLog, Part, Place, Staff, Counter
from functions import hash_password, get_jnow, datetime

WRONG_LIMIT=10

class Connection():
    def __init__(self, host='127.0.0.1', username='root', password='root'):
        self.user = Staff("admin", "admin", "admin", "admin", 3, 0, "روز قبل", 1)
        self.host = host
        self.username = username
        self.password = password
        self.connection = pymysql.connect(host=self.host, user=self.username, passwd=self.password, charset='utf8')
        self.cursor = self.connection.cursor()
        query = "CREATE SCHEMA IF NOT EXISTS `qaenpower`;"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`users` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `name` VARCHAR(64) NOT NULL, `surname` VARCHAR(64) NOT NULL, `username` VARCHAR(64) NOT NULL, `password` VARCHAR(128) NOT NULL, `access_level` TINYINT(1) NOT NULL DEFAULT 2, `wrong_times` TINYINT(2) NOT NULL DEFAULT 0, `default_date` VARCHAR(64) NOT NULL DEFAULT 'روز قبل', PRIMARY KEY (`id`), UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`parts` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `title` VARCHAR(45) NOT NULL, `order` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `title_UNIQUE` (`title` ASC) VISIBLE);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`places` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `title` VARCHAR(45) NOT NULL, `part` INT UNSIGNED NOT NULL, `order` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), INDEX `part_idx` (`part` ASC) VISIBLE, UNIQUE INDEX `place_part` (`title` ASC, `part` ASC) INVISIBLE, CONSTRAINT `part` FOREIGN KEY (`part`) REFERENCES `qaenpower`.`parts` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`counters` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `name` VARCHAR(45) NOT NULL, `type` VARCHAR(45) NOT NULL, `unit` VARCHAR(45) NULL, `default_value` VARCHAR(45) NOT NULL, `variable_name` VARCHAR(45) NOT NULL, `warning_lower_bound` DECIMAL(20,10) UNSIGNED NULL, `warning_upper_bound` DECIMAL(20,10) UNSIGNED NULL, `alarm_lower_bound` DECIMAL(20,10) UNSIGNED NULL, `alarm_upper_bound` DECIMAL(20,10) UNSIGNED NULL, `formula` VARCHAR(255) NOT NULL DEFAULT '', `part` INT UNSIGNED NOT NULL, `place` INT UNSIGNED NOT NULL, `order` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `variable_name_UNIQUE` (`variable_name` ASC) VISIBLE, UNIQUE INDEX `counter_place_part` (`name` ASC, `place` ASC, `part` ASC) VISIBLE, INDEX `part2_idx` (`part` ASC) VISIBLE, INDEX `place_idx` (`place` ASC) VISIBLE, CONSTRAINT `part2` FOREIGN KEY (`part`) REFERENCES `qaenpower`.`parts` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT, CONSTRAINT `place` FOREIGN KEY (`place`) REFERENCES `qaenpower`.`places` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`counters_log` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `value` DECIMAL(20,10) UNSIGNED NOT NULL, `workout` DECIMAL(20,10) NOT NULL, `is_broken` TINYINT(1) NOT NULL DEFAULT 0, `date_time_created` DATETIME NOT NULL, `date_time_modified` DATETIME NOT NULL, `counter_id` INT UNSIGNED NOT NULL, `user_id` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), CONSTRAINT `counter_id` FOREIGN KEY (`counter_id`) REFERENCES `qaenpower`.`counters` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE, CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `qaenpower`.`users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE);"
        self.cursor.execute(query)

    def create_user(self, name, surname, username, password):
        query = "INSERT INTO `qaenpower`.`users` (`name`, `surname`, `username`, `password`) VALUES (%s, %s, %s, %s);"
        values = name, surname, username, password # چون میخوایم پسوورد رو همین الان عوض کنیم دیگه دفعه اول الکی هشش نمیکنیم.
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT `name`, `surname`, `username`, `password`, `access_level`, `wrong_times`, `default_date`, `id` FROM `qaenpower`.`users` where username=%s;"
            values = (username, )
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            if result in [None, '', ()]:
                return ("نام کاربری یافت نشد", -1)
            self.user = Staff(*result)
            return self.update_users_password(password)
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
    
    def update_users_password(self, password):
        salt = str(self.user.id)
        password = hash_password(password, salt)
        query = "UPDATE `qaenpower`.`users` SET `password` = %s WHERE (`id` = %s);"
        values = (password, self.user.id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def login(self, username, password):
        query = "SELECT `name`, `surname`, `username`, `password`, `access_level`, `wrong_times`, `default_date`, `id` FROM `qaenpower`.`users` where username=%s;"
        values = (username, )
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result in [None, '', ()]:
            return ("نام کاربری یافت نشد", -1)
        self.user = Staff(*result)
        return self.check_is_password_right(password)
        
    def update_wrong_times(self):
        query = "UPDATE `qaenpower`.`users` SET `wrong_times` = %s WHERE (`id` = %s);"
        values = (self.user.wrong_times, self.user.id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)
    
    def update_default_date_of_user(self):
        query = "UPDATE `qaenpower`.`users` SET `default_date` = %s WHERE (`id` = %s);"
        values = (self.user.default_date, self.user.id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def create_part(self, title):
        query = "INSERT INTO `qaenpower`.`parts` (`title`, `order`) VALUES (%s, 0);"
        values = (title, )
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT * FROM `qaenpower`.`parts` where title=%s;"
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
        query = "INSERT INTO `qaenpower`.`places` (`title`, `part`, `order`) VALUES (%s, %s, 0);"
        values = title, part_id
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT * FROM `qaenpower`.`places` where title=%s AND part=%s;"
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            if result in [None, '', ()]:
                return ("مکان یافت نشد", -1)
            id=result[0]
            return self.update_place_sort(id, id)
        except pymysql.err.IntegrityError as error:
            part_id, part_name, part_sort = self.get_part_by_id(part_id)
            return (f"مکان {title} برای بخش {part_name} قبلا ثبت شده است", error)
    
    def update_place_sort(self, id, order):
        query = "UPDATE `qaenpower`.`places` SET `order` = %s WHERE (`id` = %s);"
        values = (order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def get_part_by_id(self, id):
        query = "SELECT * FROM `qaenpower`.`parts` WHERE id=%s;"
        values = (id, )
        self.cursor.execute(query, values)
        return self.cursor.fetchone()
  
    def create_counter(self, name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place):
        query = "INSERT INTO `qaenpower`.`counters` (`name`, `type`, `unit`, `default_value`, `variable_name`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `formula`, `part`, `place`, `order`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0);"
        part_id, part_title, part_sort = self.get_part_by_title(part)
        place_id, place_title, place_part_id, place_sort = self.get_place_by_title_and_part_id(place, part_id)
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
                return ("در این بخش و مکان، پارامتری با این نام قبلا ثبت شده است", 2)

    def update_counter(self, name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place):
        query = "UPDATE `qaenpower`.`counters` SET `name` = %s, `type` = %s, `unit` = %s, `default_value` = %s, `variable_name` = %s, `warning_lower_bound` = %s, `warning_upper_bound` = %s, `alarm_lower_bound` = %s, `alarm_upper_bound` = %s, `formula` = %s, `part` = %s, `place` = %s WHERE (`variable_name` = %s);"
        part_id, part_title, part_sort = self.get_part_by_title(part)
        place_id, place_title, place_part_id, place_sort = self.get_place_by_title_and_part_id(place, part_id)
        values = name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part_id, place_id, variable_name
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)


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
        query = "SELECT `title`, `id` FROM `qaenpower`.`parts` ORDER BY `order`;"
        self.cursor.execute(query)
        all_parts = []
        for part in self.cursor.fetchall():
            all_parts.append(Part(*part))
        return all_parts
    
    def get_all_places_by_part_id(self, part_id):
        query = "SELECT `qaenpower`.`places`.`title`, `qaenpower`.`places`.`part` as `part_id`, `qaenpower`.`places`.`id`, `qaenpower`.`parts`.`title` as `part_title` FROM `qaenpower`.`places` join `qaenpower`.`parts` ON (`qaenpower`.`places`.`part`=`qaenpower`.`parts`.`id`) WHERE `qaenpower`.`places`.`part`=%s ORDER BY `qaenpower`.`places`.`order`;"
        values=(part_id, )
        self.cursor.execute(query, values)
        all_places = []
        for place in self.cursor.fetchall():
            all_places.append(Place(*place))
        return all_places
    
    def get_all_counters_of_this_part_and_place(self, part_id, place_id):
        query = "SELECT `qaenpower`.`counters`.`part`, `place`, `name`, `variable_name`, `formula`, `type`, `default_value`, `unit`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `qaenpower`.`counters`.`id`, `qaenpower`.`places`.`title` as `place_title`, `qaenpower`.`parts`.`title` as `part_title` FROM `qaenpower`.`counters` join `qaenpower`.`places` ON (`qaenpower`.`counters`.`place`=`qaenpower`.`places`.`id`) join `qaenpower`.`parts` ON (`qaenpower`.`counters`.`part`=`qaenpower`.`parts`.`id`) WHERE `qaenpower`.`counters`.`part`=%s AND `place`=%s ORDER BY `qaenpower`.`parts`.`order` ASC, `qaenpower`.`places`.`order` ASC, `qaenpower`.`counters`.`order` ASC;"
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

    def create_counter_log(self, value, workout, counter_id):
        query = "INSERT INTO `qaenpower`.`counters_log` (`value`, `workout`, `date_time_created`, `counter_id`) VALUES (%s, %s, %s, %s);"
        values = (value, workout, datetime.now(), counter_id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    # الکی همینجوری داشتم مینوشتم که بعدا کارم راحت شه. گفتم شاید لازم نشه ادامه ندادم.
    # def get_counter_log_by_date_time_created(self, date_time_created):
    #     query = "SELECT * FROM `qaenpower`.`counters_log` WHERE `date_time_created`<=%s ORDER BY `date_time_created` DESC LIMIT 1;"
    #     values = (date_time_created, )
    #     self.cursor.execute(query, values)
    #     temp = self.cursor.fetchone()
    #     print(temp, type(temp))
    #     if temp == None:
    #         return temp
    #     return CounterLog(*temp)

    def get_all_counters_variable_names(self):
        query = "SELECT `variable_name` FROM `qaenpower`.`counters` ORDER BY `order`;"
        self.cursor.execute(query)
        names = []
        for item in self.cursor.fetchall():
            names.append(item[0])
        return tuple(names)
    
    def get_counter_by_variable_name(self, variable_name): 
        query = "SELECT `part`, `place`, `name`, `variable_name`, `formula`, `type`, `default_value`, `unit`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `id` FROM `qaenpower`.`counters` WHERE `variable_name`=%s;"
        values = (variable_name, )
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return Counter(*temp)
    
    def get_counter_by_id(self, id):
        query = "SELECT `part`, `place`, `name`, `variable_name`, `formula`, `type`, `default_value`, `unit`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `id` FROM `qaenpower`.`counters` WHERE `id`=%s;"
        values = (id, )
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return Counter(*temp)

    def get_current_value_of_counter_by_variable_name(self, variable_name):
        query = "SELECT `id` FROM `qaenpower`.`counters` WHERE `variable_name`=%s;"
        values = (variable_name, )
        self.cursor.execute(query, values)
        id = self.cursor.fetchone()[0]
        query = "SELECT `value` FROM `qaenpower`.`counters_log` WHERE `counter`=%s ORDER BY `date_time_created` DESC LIMIT 1;"
        values = (id, )
        self.cursor.execute(query, values)
        return self.cursor.fetchone()[0]

    def change_parts_order(self, id, order):
        query = "UPDATE `qaenpower`.`parts` SET `order` = %s WHERE (`id` = %s);"
        values=(order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def change_places_order(self, id, order):
        query = "UPDATE `qaenpower`.`places` SET `order` = %s WHERE (`id` = %s);"
        values=(order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def change_counters_order(self, id, order):
        query = "UPDATE `qaenpower`.`counters` SET `order` = %s WHERE (`id` = %s);"
        values=(order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def check_is_password_right(self, password):
        if self.user.wrong_times>=10:
            return ("نام کاربری شما مسدود شده است. به مدیر دیتابیس مراجعه نمایید", -3)
        salt = str(self.user.id)
        password = hash_password(password, salt)
        if self.user.password==password:
            self.user.wrong_times=0
            self.update_wrong_times()
            return ('ok', self.user)
        else:
            self.user.wrong_times+=1
            self.update_wrong_times()
            return (f"رمز عبور اشتباه است. دقت کنید که نمیتوانید بیش از {WRONG_LIMIT} بار پشت سر هم رمز عبور خود را اشتباه وارد کنید. تعداد فرصت های باقیمانده: {WRONG_LIMIT-self.user.wrong_times}", -2)

    def change_users_password(self, username, old_password, new_password):
        query = "SELECT `name`, `surname`, `username`, `password`, `access_level`, `wrong_times`, `default_date`, `id` FROM `qaenpower`.`users` where username=%s;"
        values = (username, )
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result in [None, '', ()]:
            return ("نام کاربری یافت نشد", -1)
        self.user = Staff(*result)
        result_message, _ = self.check_is_password_right(old_password)
        if result_message == "ok":
            return self.update_users_password(new_password)
        return (result_message, _)
    
    def get_all_counters_short_info(self):
        # query = "SELECT * FROM `qaenpower`.`counters` join `qaenpower`.`parts` join `qaenpower`.`places` WHERE `qaenpower`.`counters`.`part`=`qaenpower`.`parts`.`id` AND `qaenpower`.`counters`.`place`=`qaenpower`.`places`.`id` ORDER BY `qaenpower`.`parts`.`order`, `qaenpower`.`places`.`order`, `qaenpower`.`counters`.`order`;"
        query = "SELECT `qaenpower`.`counters`.`id`, `qaenpower`.`counters`.`name`, `qaenpower`.`places`.`title`, `qaenpower`.`parts`.`title` FROM `qaenpower`.`counters` join `qaenpower`.`parts` join `qaenpower`.`places` WHERE `qaenpower`.`counters`.`part`=`qaenpower`.`parts`.`id` AND `qaenpower`.`counters`.`place`=`qaenpower`.`places`.`id` ORDER BY `qaenpower`.`parts`.`order`, `qaenpower`.`places`.`order`, `qaenpower`.`counters`.`order`;"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_all_parameters_current_value(self, selected_date):
        query = "SELECT `id`, `variable_name` FROM `qaenpower`.`counters`;"
        self.cursor.execute(query)
        temp_dict = {}
        for item in self.cursor.fetchall():
            id = item[0]
            variable_name = item[1]
            query = "SELECT `value` FROM `qaenpower`.`counters_log` WHERE `counter`=%s AND `date_time_created`<=%s ORDER BY `date_time_created` DESC LIMIT 1;"
            values = (id, selected_date)
            self.cursor.execute(query, values)
            temp_result = self.cursor.fetchone()
            if temp_result in [None, '', ()]:
                temp_dict[variable_name]=0
            else:
                temp_dict[variable_name]=temp_result[0]
        return temp_dict

    def get_all_parameters_current_value_and_workout(self, selected_date):
        query = "SELECT `id`, `variable_name` FROM `qaenpower`.`counters`;"
        self.cursor.execute(query)
        temp_dict = {}
        for item in self.cursor.fetchall():
            id = item[0]
            variable_name = item[1]
            query = "SELECT `value`, `workout` FROM `qaenpower`.`counters_log` WHERE `counter_id`=%s AND `date_time_created`<=%s ORDER BY `date_time_created` DESC LIMIT 1;"
            values = (id, selected_date)
            self.cursor.execute(query, values)
            temp_result = self.cursor.fetchone()
            if temp_result in [None, '', ()]:
                temp_dict[variable_name]={
                    'value': 0,
                    'workout': 0
                }
            else:
                temp_dict[variable_name]={
                    'value': temp_result[0],
                    'workout': temp_result[1],
                }
        return temp_dict


if __name__ == "__main__":
    c = Connection()
