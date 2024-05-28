import pymysql
from models import ParameterLog, Part, Place, Staff, Parameter
from functions import hash_password, datetime
from ui_settings import PARAMETER_TYPES

WRONG_LIMIT=10

class Connection():
    def __init__(self, host='127.0.0.1', username='root', password='root'):
        self.user = Staff("admin", "admin", "admin", "admin", 3, 0, "روز قبل", 1)
        self.host = host
        self.username = username
        self.password = password
        self.connection = pymysql.connect(host=self.host, user=self.username, passwd=self.password, charset='utf8')
        self.cursor = self.connection.cursor()
        query = "CREATE SCHEMA IF NOT EXISTS `amar221`;"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `amar221`.`users` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `name` VARCHAR(64) NOT NULL, `surname` VARCHAR(64) NOT NULL, `username` VARCHAR(64) NOT NULL, `password` VARCHAR(128) NOT NULL, `access_level` TINYINT(1) NOT NULL DEFAULT 2, `wrong_times` TINYINT(2) NOT NULL DEFAULT 0, `default_date` VARCHAR(64) NOT NULL DEFAULT 'روز قبل', PRIMARY KEY (`id`), UNIQUE INDEX `username_UNIQUE` (`username` ASC) );"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `amar221`.`sections` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `title` VARCHAR(45) NOT NULL, `order` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `title_UNIQUE` (`title` ASC) );"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `amar221`.`places` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `title` VARCHAR(45) NOT NULL, `section` INT UNSIGNED NOT NULL, `order` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), INDEX `section_idx` (`section` ASC) , UNIQUE INDEX `place_section` (`title` ASC, `section` ASC) , CONSTRAINT `section` FOREIGN KEY (`section`) REFERENCES `amar221`.`sections` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `amar221`.`parameters` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `name` VARCHAR(45) NOT NULL, `type` VARCHAR(45) NOT NULL, `unit` VARCHAR(45) NULL, `default_value` VARCHAR(45) NOT NULL, `variable_name` VARCHAR(45) NOT NULL, `warning_lower_bound` DECIMAL(20,10) UNSIGNED NULL, `warning_upper_bound` DECIMAL(20,10) UNSIGNED NULL, `alarm_lower_bound` DECIMAL(20,10) UNSIGNED NULL, `alarm_upper_bound` DECIMAL(20,10) UNSIGNED NULL, `formula` VARCHAR(255) NOT NULL DEFAULT '', `section` INT UNSIGNED NOT NULL, `place` INT UNSIGNED NOT NULL, `order` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `variable_name_UNIQUE` (`variable_name` ASC) , UNIQUE INDEX `parameter_place_section` (`name` ASC, `place` ASC, `section` ASC) , INDEX `section2_idx` (`section` ASC) , INDEX `place_idx` (`place` ASC) , CONSTRAINT `section2` FOREIGN KEY (`section`) REFERENCES `amar221`.`sections` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT, CONSTRAINT `place` FOREIGN KEY (`place`) REFERENCES `amar221`.`places` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT);"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `amar221`.`parameters_log` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `value` DECIMAL(20,10) NOT NULL, `workout` DECIMAL(20,10) NOT NULL, `is_ok` TINYINT(1) NOT NULL DEFAULT 1, `date` DATE NOT NULL, `date_time_modified` DATETIME NOT NULL, `parameter_id` INT UNSIGNED NOT NULL, `user_id` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), CONSTRAINT `parameter_id` FOREIGN KEY (`parameter_id`) REFERENCES `amar221`.`parameters` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE, CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `amar221`.`users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE);"
        self.cursor.execute(query)
        try:
            query = "INSERT INTO `amar221`.`users` (`id`, `name`, `surname`, `username`, `password`, `access_level`) VALUES (0, 'مدیر', 'اصلی', 'admin', '559b56b2daa9bd5b0b659d534a3876bdf91fc9e108c60935534afd412551e740dcdf56130a077f8674b4d203eb28284a', 1);"
            self.cursor.execute(query)
        except:
            pass

    def create_user(self, name, surname, username, password):
        try:
            query = "SELECT `id` FROM `amar221`.`users` ORDER BY `id` DESC LIMIT 1;"
            self.cursor.execute(query)
            temp = self.cursor.fetchone()
            if temp in [None, '', ()]:
                auto_increament=1
            else:
                auto_increament = temp[0]+1
            salt = str(auto_increament)
            password = hash_password(password, salt)
            query = "INSERT INTO `amar221`.`users` (`id`, `name`, `surname`, `username`, `password`) VALUES (%s, %s, %s, %s, %s);"
            values = auto_increament, name, surname, username, password
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT `name`, `surname`, `username`, `password`, `access_level`, `wrong_times`, `default_date`, `id` FROM `amar221`.`users` where username=%s;"
            values = (username, )
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            if result in [None, '', ()]:
                return ("نام کاربری یافت نشد", -1)
            self.user = Staff(*result)
            return ('ok', 0)
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
        query = "UPDATE `amar221`.`users` SET `password` = %s WHERE (`id` = %s);"
        values = (password, self.user.id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def login(self, username, password):
        query = "SELECT `name`, `surname`, `username`, `password`, `access_level`, `wrong_times`, `default_date`, `id` FROM `amar221`.`users` where username=%s;"
        values = (username, )
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result in [None, '', ()]:
            return ("نام کاربری یافت نشد", -1)
        self.user = Staff(*result)
        return self.check_is_password_right(password)

    def update_wrong_times(self):
        query = "UPDATE `amar221`.`users` SET `wrong_times` = %s WHERE (`id` = %s);"
        values = (self.user.wrong_times, self.user.id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)
    
    def update_default_date_of_user(self):
        query = "UPDATE `amar221`.`users` SET `default_date` = %s WHERE (`id` = %s);"
        values = (self.user.default_date, self.user.id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def create_part(self, title):
        query = "INSERT INTO `amar221`.`sections` (`title`, `order`) VALUES (%s, 0);"
        values = (title, )
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT * FROM `amar221`.`sections` where title=%s;"
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            if result in [None, '', ()]:
                return ("بخش یافت نشد", -1)
            id=result[0]
            return self.update_part_sort(id, id)
        except pymysql.err.IntegrityError as error:
            return (f"بخش {title} قبلا ثبت شده است", error)

    def update_part(self, id, new_name):
        query = "UPDATE `amar221`.`sections` SET `title` = %s WHERE (`id` = %s);"
        values = (new_name, id)
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            return (f"بخش {new_name} قبلا ثبت شده است", error)
    
    def update_part_sort(self, id, order):
        query = "UPDATE `amar221`.`sections` SET `order` = %s WHERE (`id` = %s);"
        values = (order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)
    
    def delete_part(self, id):
        query = "DELETE FROM `amar221`.`sections` WHERE (`id` = %s);"
        values = (id, )
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            return (f"مکان هایی برای این بخش ثبت شده اند. جهت حذف این بخش، ابتدا باید مکان های این بخش را حذف کنید", error)

    def create_place(self, title, part_id):
        query = "INSERT INTO `amar221`.`places` (`title`, `section`, `order`) VALUES (%s, %s, 0);"
        values = (title, part_id)
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT * FROM `amar221`.`places` where title=%s AND section=%s;"
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            if result in [None, '', ()]:
                return ("مکان یافت نشد", -1)
            id=result[0]
            return self.update_place_sort(id, id)
        except pymysql.err.IntegrityError as error:
            part_id, part_name, part_sort = self.get_part_by_id(part_id)
            return (f"مکان {title} برای بخش {part_name} قبلا ثبت شده است", error)
    
    def update_place(self, id, new_name, part_id):
        query = "UPDATE `amar221`.`places` SET `title` = %s, `section` = %s WHERE (`id` = %s);"
        values = (new_name, part_id, id)
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            part_id, part_name, part_sort = self.get_part_by_id(part_id)
            return (f"مکان {new_name} برای بخش {part_name} قبلا ثبت شده است", error)

    def delete_place(self, id):
        query = "DELETE FROM `amar221`.`places` WHERE (`id` = %s);"
        values = (id, )
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            return (f"پارامترهایی برای این مکان ثبت شده اند. جهت حذف این مکان، ابتدا باید تمام پارامترهای این این مکان را حذف کنید", error)

    def update_place_sort(self, id, order):
        query = "UPDATE `amar221`.`places` SET `order` = %s WHERE (`id` = %s);"
        values = (order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def get_part_by_id(self, id):
        query = "SELECT * FROM `amar221`.`sections` WHERE id=%s;"
        values = (id, )
        self.cursor.execute(query, values)
        return self.cursor.fetchone()
  
    def create_parameter(self, name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place):
        query = "INSERT INTO `amar221`.`parameters` (`name`, `type`, `unit`, `default_value`, `variable_name`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `formula`, `section`, `place`, `order`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0);"
        part_id, part_title, part_sort = self.get_part_by_title(part)
        place_id, place_title, place_part_id, place_sort = self.get_place_by_title_and_part_id(place, part_id)
        values = name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part_id, place_id
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            temp = str(error)
            if 'parameters.variable_name_UNIQUE' in temp:
                return ("نام متغیر تکراری است", 2)
            elif 'parameters.parameter_place_section' in temp:
                return ("در این بخش و مکان، پارامتری با این نام قبلا ثبت شده است", 2)

    def update_parameter(self, name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place):
        query = "UPDATE `amar221`.`parameters` SET `name` = %s, `type` = %s, `unit` = %s, `default_value` = %s, `variable_name` = %s, `warning_lower_bound` = %s, `warning_upper_bound` = %s, `alarm_lower_bound` = %s, `alarm_upper_bound` = %s, `formula` = %s, `section` = %s, `place` = %s WHERE (`variable_name` = %s);"
        part_id, part_title, part_sort = self.get_part_by_title(part)
        place_id, place_title, place_part_id, place_sort = self.get_place_by_title_and_part_id(place, part_id)
        values = name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part_id, place_id, variable_name
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def delete_parameter(self, id):
        query = "DELETE FROM `amar221`.`parameters` WHERE (`id` = %s);"
        values = (id, )
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            return (f"لاگ هایی برای این پارامتر ثبت شده اند. از طریق این برنامه نمیتوانید این پارامتر را حذف کنید. چون در ساختار دیتابیس مشکل ایجاد میکند. مدیر دیتابیس ابتدا باید لاگ های مربوط به این پارامتر را دستی حذف کند و سپس این پارامتر قابل حذف کردن است", error)

    def get_part_by_title(self, title):
        query = "SELECT * FROM `amar221`.`sections` WHERE title=%s;"
        self.cursor.execute(query, title)
        return self.cursor.fetchone()
 
    def get_place_by_title_and_part_id(self, title, part_id):
        query = "SELECT * FROM `amar221`.`places` WHERE title=%s AND section=%s;"
        values = title, part_id
        self.cursor.execute(query, values)
        return self.cursor.fetchone()

    def get_all_parts(self):
        query = "SELECT `title`, `id` FROM `amar221`.`sections` ORDER BY `order`;"
        self.cursor.execute(query)
        all_parts = []
        for part in self.cursor.fetchall():
            all_parts.append(Part(*part))
        return all_parts

    def get_all_places_by_part_id(self, part_id):
        query = "SELECT `amar221`.`places`.`title`, `amar221`.`places`.`section` as `section_id`, `amar221`.`places`.`id`, `amar221`.`sections`.`title` as `section_title` FROM `amar221`.`places` join `amar221`.`sections` ON (`amar221`.`places`.`section`=`amar221`.`sections`.`id`) WHERE `amar221`.`places`.`section`=%s ORDER BY `amar221`.`places`.`order`;"
        values=(part_id, )
        self.cursor.execute(query, values)
        all_places = []
        for place in self.cursor.fetchall():
            all_places.append(Place(*place))
        return all_places
    
    def get_last_log_of_parameter_by_id(self, id):
        query = "SELECT `date` FROM `amar221`.`parameters_log` WHERE `parameter_id`=%s ORDER BY `date` DESC LIMIT 1;"
        values = (id, )
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return temp[0]

    def get_all_parameters_of_this_part_and_place(self, part_id, place_id):
        query = "SELECT `amar221`.`parameters`.`section`, `place`, `name`, `variable_name`, `formula`, `type`, `default_value`, `unit`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `amar221`.`parameters`.`id`, `amar221`.`places`.`title` as `place_title`, `amar221`.`sections`.`title` as `section_title` FROM `amar221`.`parameters` join `amar221`.`places` ON (`amar221`.`parameters`.`place`=`amar221`.`places`.`id`) join `amar221`.`sections` ON (`amar221`.`parameters`.`section`=`amar221`.`sections`.`id`) WHERE `amar221`.`parameters`.`section`=%s AND `place`=%s ORDER BY `amar221`.`sections`.`order` ASC, `amar221`.`places`.`order` ASC, `amar221`.`parameters`.`order` ASC;"
        values = part_id, place_id
        self.cursor.execute(query, values)
        parameters = []
        for parameter in self.cursor.fetchall():
            t = Parameter(*parameter)
            parameters.append(t)
        return parameters

    def get_place_name_by_id_and_part_id(self, title, part_id):
        query = "SELECT * FROM `amar221`.`places` WHERE title=%s AND section=%s;"
        values = title, part_id
        self.cursor.execute(query, values)
        return self.cursor.fetchone()

    def create_parameter_log(self, value, workout, is_ok, date, parameter_id, user_id):
        query = "INSERT INTO `amar221`.`parameters_log` (`value`, `workout`, `is_ok`, `date`, `date_time_modified`, `parameter_id`, `user_id`) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        values = (value, workout, is_ok, date, datetime.now(), parameter_id, user_id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def update_parameter_log(self, value, workout, is_ok, date, parameter_id, user_id):
        query = "SELECT `id` FROM `amar221`.`parameters_log` WHERE `parameter_id`=%s AND `date`<=%s ORDER BY `date` DESC LIMIT 1;"
        values = (parameter_id, date)
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone() # پارامتری هایی که از قبل وجود دارند، لاگ هم دارند. اما ممکنه برای یک مکان پارامتر جدیدی اضافه بشه که لاگ قبلی نداره. در این صورت پس برای این پارامتر هیچ جوابی نمیده و این طوری به ارور میخوریم. پس در این حالت میگیم براش بسازه و آپدیت نکنه.
        if temp in [None, '', ()]:
            return self.create_parameter_log(value, workout, is_ok, date, parameter_id, user_id)
        parameter_log_id=temp[0]
        query = "UPDATE `amar221`.`parameters_log` SET `value` = %s, `workout` = %s, `is_ok` = %s, `date_time_modified` = %s, `user_id` = %s WHERE (`id` = %s);"
        values = (value, workout, is_ok, datetime.now(), user_id, parameter_log_id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def get_parameter_log_by_parameter_id_and_date(self, parameter_id, date):
        query = "SELECT `value`, `workout`, `is_ok`, `date`, `date_time_modified`, `parameter_id`, `user_id`, `amar221`.`parameters_log`.`id`, `amar221`.`users`.`name` as `users_name`, `amar221`.`users`.`surname` as `users_surname` FROM `amar221`.`parameters_log` join `amar221`.`users` ON (`amar221`.`parameters_log`.`user_id`=`amar221`.`users`.`id`)  WHERE `parameter_id`=%s AND `date`<=%s ORDER BY `date` DESC LIMIT 1;"
        values = (parameter_id, date)
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return ParameterLog(*temp)

    def get_parameters_log_by_date(self, date):
        query = "SELECT `id`, `variable_name` FROM `amar221`.`parameters`;"
        self.cursor.execute(query)
        temp_dict = {}
        for item in self.cursor.fetchall():
            id = item[0]
            variable_name = item[1]
            query = "SELECT `value`, `workout`, `is_ok`, `date`, `date_time_modified`, `parameter_id`, `user_id`, `amar221`.`parameters_log`.`id`, `amar221`.`users`.`name` as `users_name`, `amar221`.`users`.`surname` as `users_surname` FROM `amar221`.`parameters_log` join `amar221`.`users` ON (`amar221`.`parameters_log`.`user_id`=`amar221`.`users`.`id`) WHERE `amar221`.`parameters_log`.`parameter_id`=%s AND `date`<=%s ORDER BY `date` DESC LIMIT 1"
            values = (id, date)
            self.cursor.execute(query, values)
            temp = self.cursor.fetchone()
            if temp == None:
                temp_dict[variable_name] = None
            else:
                temp_dict[variable_name] = ParameterLog(*temp)
        return temp_dict
    
    def get_parameters_next_log_by_date(self, date):
        query = "SELECT `id`, `variable_name` FROM `amar221`.`parameters`;"
        self.cursor.execute(query)
        temp_dict = {}
        for item in self.cursor.fetchall():
            id = item[0]
            variable_name = item[1]
            query = "SELECT `value`, `workout`, `is_ok`, `date`, `date_time_modified`, `parameter_id`, `user_id`, `amar221`.`parameters_log`.`id`, `amar221`.`users`.`name` as `users_name`, `amar221`.`users`.`surname` as `users_surname`, `amar221`.`parameters`.`type` FROM `amar221`.`parameters_log` JOIN `amar221`.`users` ON (`amar221`.`parameters_log`.`user_id`=`amar221`.`users`.`id`) JOIN `amar221`.`parameters` ON (`amar221`.`parameters_log`.`parameter_id`=`amar221`.`parameters`.`id`) WHERE `amar221`.`parameters_log`.`parameter_id`=%s AND `date`>%s ORDER BY `date` ASC LIMIT 1;"
            values = (id, date)
            self.cursor.execute(query, values)
            temp = self.cursor.fetchone()
            if temp == None:
                temp_dict[variable_name] = None
            else:
                temp_dict[variable_name] = ParameterLog(*temp)
        return temp_dict
    
    def change_log_by_computer_id(self, log:ParameterLog):
        if log.type==PARAMETER_TYPES[2]: # برای محاسباتی ها، مقدار ولیو و ورک اوت با یک مقدار ثبت میشن
            query = "UPDATE `amar221`.`parameters_log` SET `value` = %s, `workout` = %s, `date_time_modified` = %s, `user_id` = %s WHERE (`id` = %s);"
            values = (log.workout, log.workout, datetime.now(), log.user_id, log.id)
        elif log.type==PARAMETER_TYPES[1]: # پارامترهای ثابت لازم نیست تغییر داده بشن
            return ("ok", 0)
        elif log.type==PARAMETER_TYPES[0] and log.is_ok==False: # پارامترهای از جنس کنتور که خراب بودن لازم نیست تغییر داده بشن. مقدار ورک اوتشون دستی وارد شده بود
            return ("ok", 0)
        elif log.type==PARAMETER_TYPES[0] and log.is_ok:
            query = "UPDATE `amar221`.`parameters_log` SET `workout` = %s, `date_time_modified` = %s, `user_id` = %s WHERE (`id` = %s);"
            values = (log.workout, datetime.now(), log.user_id, log.id)
            # دقت کنم که تو این حالت به مقدارش ما دست نمیزنیم. چون مقدارش قبلا ثبت شده و فقط کارکردش رو
            # حساب میکنیم. اگه مقدار عوض بشه همینطوری زنجیروار تا روز آخر باید عوض کنیم همه رو
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def get_previous_value_of_parameter_by_id_and_date(self, id, date):
        query = "SELECT `value` FROM `amar221`.`parameters_log` WHERE `parameter_id`=%s AND `date`<=%s ORDER BY `date` DESC LIMIT 2"
        values = (id, date)
        self.cursor.execute(query, values)
        self.cursor.fetchone() # این مهم نیست. الکی میگیریم میندازیمش دور
        value = self.cursor.fetchone()
        if value == None: # یعنی کلا یه رکورد تو دیتابیس بوده. پس قبل از اون میشه ۰
            return 0
        return value[0]
        

    def get_all_parameters_variable_names(self):
        query = "SELECT `variable_name` FROM `amar221`.`parameters` ORDER BY `order`;"
        self.cursor.execute(query)
        names = []
        for item in self.cursor.fetchall():
            names.append(item[0])
        return tuple(names)
    
    def get_parameter_by_variable_name(self, variable_name): 
        query = "SELECT `section`, `place`, `name`, `variable_name`, `formula`, `type`, `default_value`, `unit`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `id` FROM `amar221`.`parameters` WHERE `variable_name`=%s;"
        values = (variable_name, )
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return Parameter(*temp)
    
    def get_parameter_by_id(self, id):
        query = "SELECT `section`, `place`, `name`, `variable_name`, `formula`, `type`, `default_value`, `unit`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `id` FROM `amar221`.`parameters` WHERE `id`=%s;"
        values = (id, )
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return Parameter(*temp)

    def get_current_value_of_parameter_by_variable_name(self, variable_name):
        query = "SELECT `id` FROM `amar221`.`parameters` WHERE `variable_name`=%s;"
        values = (variable_name, )
        self.cursor.execute(query, values)
        id = self.cursor.fetchone()[0]
        query = "SELECT `value` FROM `amar221`.`parameters_log` WHERE `parameter`=%s ORDER BY `date` DESC LIMIT 1;"
        values = (id, )
        self.cursor.execute(query, values)
        return self.cursor.fetchone()[0]

    def change_parts_order(self, id, order):
        query = "UPDATE `amar221`.`sections` SET `order` = %s WHERE (`id` = %s);"
        values=(order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def change_places_order(self, id, order):
        query = "UPDATE `amar221`.`places` SET `order` = %s WHERE (`id` = %s);"
        values=(order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def change_parameters_order(self, id, order):
        query = "UPDATE `amar221`.`parameters` SET `order` = %s WHERE (`id` = %s);"
        values=(order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def check_is_password_right(self, password):
        if self.user.wrong_times>=WRONG_LIMIT:
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
        query = "SELECT `name`, `surname`, `username`, `password`, `access_level`, `wrong_times`, `default_date`, `id` FROM `amar221`.`users` where username=%s;"
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
    
    def get_all_parameters_short_info(self):
        # query = "SELECT * FROM `amar221`.`parameters` join `amar221`.`sections` join `amar221`.`places` WHERE `amar221`.`parameters`.`section`=`amar221`.`sections`.`id` AND `amar221`.`parameters`.`place`=`amar221`.`places`.`id` ORDER BY `amar221`.`sections`.`order`, `amar221`.`places`.`order`, `amar221`.`parameters`.`order`;"
        query = "SELECT `amar221`.`parameters`.`id`, `amar221`.`parameters`.`name`, `amar221`.`places`.`title`, `amar221`.`sections`.`title` FROM `amar221`.`parameters` join `amar221`.`sections` join `amar221`.`places` WHERE `amar221`.`parameters`.`section`=`amar221`.`sections`.`id` AND `amar221`.`parameters`.`place`=`amar221`.`places`.`id` ORDER BY `amar221`.`sections`.`order`, `amar221`.`places`.`order`, `amar221`.`parameters`.`order`;"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_all_parameters_current_value(self, selected_date):
        query = "SELECT `id`, `variable_name` FROM `amar221`.`parameters`;"
        self.cursor.execute(query)
        temp_dict = {}
        for item in self.cursor.fetchall():
            id = item[0]
            variable_name = item[1]
            query = "SELECT `value` FROM `amar221`.`parameters_log` WHERE `parameter`=%s AND `date`<=%s ORDER BY `date` DESC LIMIT 1;"
            values = (id, selected_date)
            self.cursor.execute(query, values)
            temp_result = self.cursor.fetchone()
            if temp_result in [None, '', ()]:
                temp_dict[variable_name]=0
            else:
                temp_dict[variable_name]=temp_result[0]
        return temp_dict

    def get_all_parameters_current_value_and_workout(self, selected_date):
        query = "SELECT `id`, `variable_name` FROM `amar221`.`parameters`;"
        self.cursor.execute(query)
        temp_dict = {}
        for item in self.cursor.fetchall():
            id = item[0]
            variable_name = item[1]
            query = "SELECT `value`, `workout` FROM `amar221`.`parameters_log` WHERE `parameter_id`=%s AND `date`<=%s ORDER BY `date` DESC LIMIT 1;"
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
    
    def get_all_parameters_formula(self):
        query = "SELECT `formula` FROM `amar221`.`parameters`;"
        self.cursor.execute(query)
        formulas = []
        for formula in self.cursor.fetchall():
            formulas.append(formula[0])
        return formulas

if __name__ == "__main__":
    c = Connection()
