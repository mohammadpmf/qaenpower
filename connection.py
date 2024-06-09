import pymysql
from models import ParameterLog, Part, Place, Staff, Parameter
from functions import hash_password, datetime
from ui_settings import PARAMETER_TYPES

WRONG_LIMIT=10

class Connection():
    def __init__(self, host='127.0.0.1', username='root', password='root', db='amar'):
        self.user = Staff("admin", "admin", "admin", "admin", 3, 0, "روز قبل", 1)
        self.host = host
        self.db=db
        self.username = username
        self.password = password
        self.connection = pymysql.connect(host=self.host, user=self.username, passwd=self.password, database=self.db, charset='utf8')
        self.cursor = self.connection.cursor()
        # query = "CREATE SCHEMA IF NOT EXISTS `amar`;"
        # self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `tbl_users` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `name` VARCHAR(64) NOT NULL, `surname` VARCHAR(64) NOT NULL, `username` VARCHAR(64) NOT NULL, `password` VARCHAR(128) NOT NULL, `access_level` TINYINT(1) NOT NULL DEFAULT 2, `wrong_times` TINYINT(2) NOT NULL DEFAULT 0, `default_date` VARCHAR(64) NOT NULL DEFAULT 'روز قبل', PRIMARY KEY (`id`), UNIQUE INDEX `username_UNIQUE` (`username` ASC)) ENGINE = MyISAM;"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `tbl_sections` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `title` VARCHAR(45) NOT NULL, `order` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `title_UNIQUE` (`title` ASC)) ENGINE = MyISAM;"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `tbl_places` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `title` VARCHAR(45) NOT NULL, `section` INT UNSIGNED NOT NULL, `order` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), INDEX `section_idx` (`section` ASC) , UNIQUE INDEX `place_section` (`title` ASC, `section` ASC) , CONSTRAINT `section` FOREIGN KEY (`section`) REFERENCES `tbl_sections` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT) ENGINE = MyISAM;"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `tbl_parameters` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `name` VARCHAR(45) NOT NULL, `type` VARCHAR(45) NOT NULL, `unit` VARCHAR(45) NULL, `default_value` VARCHAR(45) NOT NULL, `variable_name` VARCHAR(45) NOT NULL, `warning_lower_bound` DECIMAL(20,10) UNSIGNED NULL, `warning_upper_bound` DECIMAL(20,10) UNSIGNED NULL, `alarm_lower_bound` DECIMAL(20,10) UNSIGNED NULL, `alarm_upper_bound` DECIMAL(20,10) UNSIGNED NULL, `formula` VARCHAR(255) NOT NULL DEFAULT '', `section` INT UNSIGNED NOT NULL, `place` INT UNSIGNED NOT NULL, `order` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `variable_name_UNIQUE` (`variable_name` ASC) , UNIQUE INDEX `parameter_place_section` (`name` ASC, `place` ASC, `section` ASC) , INDEX `section2_idx` (`section` ASC) , INDEX `place_idx` (`place` ASC) , CONSTRAINT `section2` FOREIGN KEY (`section`) REFERENCES `tbl_sections` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT, CONSTRAINT `place` FOREIGN KEY (`place`) REFERENCES `tbl_places` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT) ENGINE = MyISAM;"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `tbl_parameters_log` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `value` DECIMAL(20,10) NOT NULL, `workout` DECIMAL(20,10) NOT NULL, `is_ok` TINYINT(1) NOT NULL DEFAULT 1, `date` DATE NOT NULL, `date_time_modified` DATETIME NOT NULL, `parameter_id` INT UNSIGNED NOT NULL, `user_id` INT UNSIGNED NOT NULL, PRIMARY KEY (`id`), INDEX `date_index` (`date` ASC), CONSTRAINT `parameter_id` FOREIGN KEY (`parameter_id`) REFERENCES `tbl_parameters` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE, CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `tbl_users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE) ENGINE = MyISAM;"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `tbl_parameters_max_date` (`id` INT NOT NULL AUTO_INCREMENT, `parameter_id` INT UNSIGNED NOT NULL, `max_date` DATE NOT NULL, PRIMARY KEY (`id`)) ENGINE = MEMORY;"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `tbl_parameters_min_date` (`id` INT NOT NULL AUTO_INCREMENT, `parameter_id` INT UNSIGNED NOT NULL, `min_date` DATE NOT NULL, PRIMARY KEY (`id`)) ENGINE = MEMORY;"
        self.cursor.execute(query)
        try:
            query = "INSERT INTO `tbl_users` (`id`, `name`, `surname`, `username`, `password`, `access_level`) VALUES (0, 'مدیر', 'اصلی', 'admin', '559b56b2daa9bd5b0b659d534a3876bdf91fc9e108c60935534afd412551e740dcdf56130a077f8674b4d203eb28284a', 1);"
            self.cursor.execute(query)
        except:
            pass

    def create_user(self, name, surname, username, password):
        try:
            query = "SELECT `id` FROM `tbl_users` ORDER BY `id` DESC LIMIT 1;"
            self.cursor.execute(query)
            temp = self.cursor.fetchone()
            if temp in [None, '', ()]:
                auto_increament=1
            else:
                auto_increament = temp[0]+1
            salt = str(auto_increament)
            password = hash_password(password, salt)
            query = "INSERT INTO `tbl_users` (`id`, `name`, `surname`, `username`, `password`) VALUES (%s, %s, %s, %s, %s);"
            values = auto_increament, name, surname, username, password
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT `name`, `surname`, `username`, `password`, `access_level`, `wrong_times`, `default_date`, `id` FROM `tbl_users` where username=%s;"
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
        query = "UPDATE `tbl_users` SET `password` = %s WHERE (`id` = %s);"
        values = (password, self.user.id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def login(self, username, password):
        query = "SELECT `name`, `surname`, `username`, `password`, `access_level`, `wrong_times`, `default_date`, `id` FROM `tbl_users` where username=%s;"
        values = (username, )
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result in [None, '', ()]:
            return ("نام کاربری یافت نشد", -1)
        self.user = Staff(*result)
        return self.check_is_password_right(password)

    def update_wrong_times(self):
        query = "UPDATE `tbl_users` SET `wrong_times` = %s WHERE (`id` = %s);"
        values = (self.user.wrong_times, self.user.id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)
    
    def update_default_date_of_user(self):
        query = "UPDATE `tbl_users` SET `default_date` = %s WHERE (`id` = %s);"
        values = (self.user.default_date, self.user.id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def create_part(self, title):
        query = "INSERT INTO `tbl_sections` (`title`, `order`) VALUES (%s, 0);"
        values = (title, )
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT * FROM `tbl_sections` where title=%s;"
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()
            if result in [None, '', ()]:
                return ("بخش یافت نشد", -1)
            id=result[0]
            return self.update_part_sort(id, id)
        except pymysql.err.IntegrityError as error:
            return (f"بخش {title} قبلا ثبت شده است", error)

    def update_part(self, id, new_name):
        query = "UPDATE `tbl_sections` SET `title` = %s WHERE (`id` = %s);"
        values = (new_name, id)
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            return (f"بخش {new_name} قبلا ثبت شده است", error)
    
    def update_part_sort(self, id, order):
        query = "UPDATE `tbl_sections` SET `order` = %s WHERE (`id` = %s);"
        values = (order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)
    
    def delete_part(self, id):
        query = "SELECT * FROM `tbl_places` WHERE (`section` = %s);"
        values = (id, )
        self.cursor.execute(query, values)
        res = self.cursor.fetchone()
        if res!=None:
            return (f"مکان هایی برای این بخش ثبت شده اند. جهت حذف این بخش، ابتدا باید مکان های این بخش را حذف کنید", 2)
        query = "DELETE FROM `tbl_sections` WHERE (`id` = %s);"
        values = (id, )
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def create_place(self, title, part_id):
        query = "INSERT INTO `tbl_places` (`title`, `section`, `order`) VALUES (%s, %s, 0);"
        values = (title, part_id)
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            query = "SELECT * FROM `tbl_places` where title=%s AND section=%s;"
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
        query = "UPDATE `tbl_places` SET `title` = %s, `section` = %s WHERE (`id` = %s);"
        values = (new_name, part_id, id)
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            part_id, part_name, part_sort = self.get_part_by_id(part_id)
            return (f"مکان {new_name} برای بخش {part_name} قبلا ثبت شده است", error)

    def delete_place(self, id):
        query = "SELECT * FROM `tbl_parameters` WHERE (`place` = %s);"
        values = (id, )
        self.cursor.execute(query, values)
        res = self.cursor.fetchone()
        if res!=None:
            return (f"پارامترهایی برای این مکان ثبت شده اند. جهت حذف این مکان، ابتدا باید تمام پارامترهای این این مکان را حذف کنید", 2)
        query = "DELETE FROM `tbl_places` WHERE (`id` = %s);"
        values = (id, )
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def update_place_sort(self, id, order):
        query = "UPDATE `tbl_places` SET `order` = %s WHERE (`id` = %s);"
        values = (order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def get_part_by_id(self, id):
        query = "SELECT * FROM `tbl_sections` WHERE id=%s;"
        values = (id, )
        self.cursor.execute(query, values)
        return self.cursor.fetchone()
  
    def create_parameter(self, name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place):
        query = "INSERT INTO `tbl_parameters` (`name`, `type`, `unit`, `default_value`, `variable_name`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `formula`, `section`, `place`, `order`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0);"
        part_id, part_title, part_sort = self.get_part_by_title(part)
        place_id, place_title, place_part_id, place_sort = self.get_place_by_title_and_part_id(place, part_id)
        values = name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part_id, place_id
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return ("ok", 0)
        except pymysql.err.IntegrityError as error:
            temp = str(error)
            if 'tbl_parameters.variable_name_UNIQUE' in temp:
                return ("نام متغیر تکراری است", 2)
            elif 'tbl_parameters.parameter_place_section' in temp:
                return ("در این بخش و مکان، پارامتری با این نام قبلا ثبت شده است", 2)

    def update_parameter(self, name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part, place):
        query = "UPDATE `tbl_parameters` SET `name` = %s, `type` = %s, `unit` = %s, `default_value` = %s, `variable_name` = %s, `warning_lower_bound` = %s, `warning_upper_bound` = %s, `alarm_lower_bound` = %s, `alarm_upper_bound` = %s, `formula` = %s, `section` = %s, `place` = %s WHERE (`variable_name` = %s);"
        part_id, part_title, part_sort = self.get_part_by_title(part)
        place_id, place_title, place_part_id, place_sort = self.get_place_by_title_and_part_id(place, part_id)
        values = name, type, unit, default_value, variable_name, warning_lower_bound, warning_upper_bound, alarm_lower_bound, alarm_upper_bound, formula, part_id, place_id, variable_name
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def delete_parameter(self, id):
        query = "SELECT * FROM `tbl_parameters_log` WHERE `parameter_id`=%s;"
        values = (id, )
        self.cursor.execute(query, values)
        res = self.cursor.fetchone()
        if res!=None:
            return (f"لاگ هایی برای این پارامتر ثبت شده اند. از طریق این برنامه نمیتوانید این پارامتر را حذف کنید. چون در ساختار دیتابیس مشکل ایجاد میکند. مدیر دیتابیس ابتدا باید لاگ های مربوط به این پارامتر را دستی حذف کند و سپس این پارامتر قابل حذف کردن است", 2)
        query = "DELETE FROM `tbl_parameters` WHERE (`id` = %s);"
        values = (id, )
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def get_part_by_title(self, title):
        query = "SELECT * FROM `tbl_sections` WHERE title=%s;"
        self.cursor.execute(query, title)
        return self.cursor.fetchone()
 
    def get_place_by_title_and_part_id(self, title, part_id):
        query = "SELECT * FROM `tbl_places` WHERE title=%s AND section=%s;"
        values = title, part_id
        self.cursor.execute(query, values)
        return self.cursor.fetchone()

    def get_all_parts(self):
        query = "SELECT `title`, `id` FROM `tbl_sections` ORDER BY `order`;"
        self.cursor.execute(query)
        all_parts = []
        for part in self.cursor.fetchall():
            all_parts.append(Part(*part))
        return all_parts

    def get_all_places_by_part_id(self, part_id):
        query = "SELECT `tbl_places`.`title`, `tbl_places`.`section` as `section_id`, `tbl_places`.`id`, `tbl_sections`.`title` as `section_title` FROM `tbl_places` join `tbl_sections` ON (`tbl_places`.`section`=`tbl_sections`.`id`) WHERE `tbl_places`.`section`=%s ORDER BY `tbl_places`.`order`;"
        values=(part_id, )
        self.cursor.execute(query, values)
        all_places = []
        for place in self.cursor.fetchall():
            all_places.append(Place(*place))
        return all_places
    
    def get_last_log_date_of_part_by_part_id(self, id):
        query = "SELECT `date` FROM `tbl_parameters` JOIN `tbl_parameters_log` ON (`tbl_parameters`.`id`=`tbl_parameters_log`.`parameter_id`) WHERE `section`=%s ORDER BY `date` DESC LIMIT 1;"
        values = (id, )
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return temp[0]

    def get_last_log_of_parameter_by_id(self, id):
        query = "SELECT `date` FROM `tbl_parameters_log` WHERE `parameter_id`=%s ORDER BY `date` DESC LIMIT 1;"
        values = (id, )
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return temp[0]

    def get_all_parameters_of_this_part_and_place(self, part_id, place_id):
        query = "SELECT `tbl_parameters`.`section`, `place`, `name`, `variable_name`, `formula`, `type`, `default_value`, `unit`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `tbl_parameters`.`id`, `tbl_places`.`title` as `place_title`, `tbl_sections`.`title` as `section_title` FROM `tbl_parameters` join `tbl_places` ON (`tbl_parameters`.`place`=`tbl_places`.`id`) join `tbl_sections` ON (`tbl_parameters`.`section`=`tbl_sections`.`id`) WHERE `tbl_parameters`.`section`=%s AND `place`=%s ORDER BY `tbl_sections`.`order` ASC, `tbl_places`.`order` ASC, `tbl_parameters`.`order` ASC;"
        values = part_id, place_id
        self.cursor.execute(query, values)
        tbl_parameters = []
        for parameter in self.cursor.fetchall():
            t = Parameter(*parameter)
            tbl_parameters.append(t)
        return tbl_parameters

    def get_place_name_by_id_and_part_id(self, title, part_id):
        query = "SELECT * FROM `tbl_places` WHERE title=%s AND section=%s;"
        values = title, part_id
        self.cursor.execute(query, values)
        return self.cursor.fetchone()

    def create_parameter_log(self, value, workout, is_ok, date, parameter_id, user_id):
        query = "INSERT INTO `tbl_parameters_log` (`value`, `workout`, `is_ok`, `date`, `date_time_modified`, `parameter_id`, `user_id`) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        values = (value, workout, is_ok, date, datetime.now(), parameter_id, user_id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def update_parameter_log(self, value, workout, is_ok, date, parameter_id, user_id):
        query = "SELECT `id` FROM `tbl_parameters_log` WHERE `parameter_id`=%s AND `date`<=%s ORDER BY `date` DESC LIMIT 1;"
        values = (parameter_id, date)
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone() # پارامتری هایی که از قبل وجود دارند، لاگ هم دارند. اما ممکنه برای یک مکان پارامتر جدیدی اضافه بشه که لاگ قبلی نداره. در این صورت پس برای این پارامتر هیچ جوابی نمیده و این طوری به ارور میخوریم. پس در این حالت میگیم براش بسازه و آپدیت نکنه.
        if temp in [None, '', ()]:
            return self.create_parameter_log(value, workout, is_ok, date, parameter_id, user_id)
        parameter_log_id=temp[0]
        query = "UPDATE `tbl_parameters_log` SET `value` = %s, `workout` = %s, `is_ok` = %s, `date_time_modified` = %s, `user_id` = %s WHERE (`id` = %s);"
        values = (value, workout, is_ok, datetime.now(), user_id, parameter_log_id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def get_parameter_log_by_parameter_id_and_date(self, parameter_id, date):
        query = "SELECT `value`, `workout`, `is_ok`, `date`, `date_time_modified`, `parameter_id`, `user_id`, `tbl_parameters_log`.`id`, `tbl_users`.`name` as `users_name`, `tbl_users`.`surname` as `users_surname` FROM `tbl_parameters_log` join `tbl_users` ON (`tbl_parameters_log`.`user_id`=`tbl_users`.`id`)  WHERE `parameter_id`=%s AND `date`<=%s ORDER BY `date` DESC LIMIT 1;"
        values = (parameter_id, date)
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return ParameterLog(*temp)

    def get_parameters_log_by_date(self, date) -> dict[ParameterLog|None]:
        self.set_max_date_into_temp_table(date)
        query = "SELECT `value`, `workout`, `is_ok`, `date`, `date_time_modified`, `tbl_parameters_log`.`parameter_id`, `tbl_parameters_log`.`user_id`, `tbl_parameters_log`.`id`, `tbl_users`.`name` AS `users_name`, `tbl_users`.`surname` AS `users_surname`, `tbl_parameters`.`type`, `tbl_parameters`.`variable_name` FROM (`tbl_parameters` JOIN `tbl_parameters_max_date` ON (`tbl_parameters`.`id`=`tbl_parameters_max_date`.`parameter_id`)) JOIN `tbl_parameters_log` ON (`tbl_parameters`.`id`=`tbl_parameters_log`.`parameter_id` AND `tbl_parameters_max_date`.`max_date`=`tbl_parameters_log`.`date`) JOIN `tbl_users` ON (`tbl_parameters_log`.`user_id`=`tbl_users`.`id`);"
        self.cursor.execute(query)
        temp_dict = {}
        for item in self.cursor.fetchall():
            variable_name = item[11]
            temp_dict[variable_name] = ParameterLog(*item[:-1])
        query = "SELECT `id`, `variable_name` FROM `tbl_parameters`;"
        self.cursor.execute(query)
        for item in self.cursor.fetchall():
            variable_name=item[1]
            try:
                temp_dict[variable_name] # هیچ استفاده ای ازش نکردم. فقط برای این که ببینم هست یا نه به جای نوشتن ایف، گفتم که این کلید رو از تو دیکشنری در بیاره. اگه بود که هیچی. اگه نبود خواست ارور بده گفتم یکی بسازه با مقدار نان
            except KeyError:
                temp_dict[variable_name]=None
            # اگر لاگی نداشت، تو برنامه نباید ارور کلید بده. در هر حال اون وریبل وجود داره. اما
            # فقط مقدارش خالیه. به خاطر همین موقع دادن ارور کلید مقدارش رو نان گذاشتم.
        return temp_dict
    
    def get_parameters_next_log_by_date(self, date):
        self.set_min_date_into_temp_table(date)
        query = "SELECT `value`, `workout`, `is_ok`, `date`, `date_time_modified`, `tbl_parameters_log`.`parameter_id`, `tbl_parameters_log`.`user_id`, `tbl_parameters_log`.`id`, `tbl_users`.`name` AS `users_name`, `tbl_users`.`surname` AS `users_surname`, `tbl_parameters`.`type`, `tbl_parameters`.`variable_name` FROM (`tbl_parameters` JOIN `tbl_parameters_min_date` ON (`tbl_parameters`.`id`=`tbl_parameters_min_date`.`parameter_id`)) JOIN `tbl_parameters_log` ON (`tbl_parameters`.`id`=`tbl_parameters_log`.`parameter_id` AND `tbl_parameters_min_date`.`min_date`=`tbl_parameters_log`.`date`) JOIN `tbl_users` ON (`tbl_parameters_log`.`user_id`=`tbl_users`.`id`);"
        self.cursor.execute(query)
        temp_dict = {}
        for item in self.cursor.fetchall():
            variable_name = item[11]
            temp_dict[variable_name] = ParameterLog(*item[:-1])
        query = "SELECT `id`, `variable_name` FROM `tbl_parameters`;"
        self.cursor.execute(query)
        for item in self.cursor.fetchall():
            variable_name=item[1]
            try:
                temp_dict[variable_name]
            except KeyError:
                temp_dict[variable_name]=None
        return temp_dict
    
    def change_log_by_computer_id(self, log:ParameterLog):
        if log.type==PARAMETER_TYPES[2]: # برای محاسباتی ها، مقدار ولیو و ورک اوت با یک مقدار ثبت میشن
            query = "UPDATE `tbl_parameters_log` SET `value` = %s, `workout` = %s, `date_time_modified` = %s, `user_id` = %s WHERE (`id` = %s);"
            values = (log.workout, log.workout, datetime.now(), log.user_id, log.id)
        elif log.type==PARAMETER_TYPES[1]: # پارامترهای ثابت لازم نیست تغییر داده بشن
            return ("ok", 0)
        elif log.type==PARAMETER_TYPES[0] and log.is_ok==False: # پارامترهای از جنس کنتور که خراب بودن لازم نیست تغییر داده بشن. مقدار ورک اوتشون دستی وارد شده بود
            return ("ok", 0)
        elif log.type==PARAMETER_TYPES[0] and log.is_ok:
            query = "UPDATE `tbl_parameters_log` SET `workout` = %s, `date_time_modified` = %s, `user_id` = %s WHERE (`id` = %s);"
            values = (log.workout, datetime.now(), log.user_id, log.id)
            # دقت کنم که تو این حالت به مقدارش ما دست نمیزنیم. چون مقدارش قبلا ثبت شده و فقط کارکردش رو
            # حساب میکنیم. اگه مقدار عوض بشه همینطوری زنجیروار تا روز آخر باید عوض کنیم همه رو
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def get_previous_value_of_parameter_by_id_and_date(self, id, date):
        query = "SELECT `value` FROM `tbl_parameters_log` WHERE `parameter_id`=%s AND `date`<=%s ORDER BY `date` DESC LIMIT 2"
        values = (id, date)
        self.cursor.execute(query, values)
        self.cursor.fetchone() # این مهم نیست. الکی میگیریم میندازیمش دور
        value = self.cursor.fetchone()
        if value == None: # یعنی کلا یه رکورد تو دیتابیس بوده. پس قبل از اون میشه ۰
            return 0
        return value[0]
        

    def get_all_parameters_variable_names(self):
        query = "SELECT `variable_name` FROM `tbl_parameters` ORDER BY `order`;"
        self.cursor.execute(query)
        names = []
        for item in self.cursor.fetchall():
            names.append(item[0])
        return tuple(names)
    
    def get_parameter_by_variable_name(self, variable_name): 
        query = "SELECT `section`, `place`, `name`, `variable_name`, `formula`, `type`, `default_value`, `unit`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `id` FROM `tbl_parameters` WHERE `variable_name`=%s;"
        values = (variable_name, )
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return Parameter(*temp)
    
    def get_parameter_by_id(self, id):
        query = "SELECT `section`, `place`, `name`, `variable_name`, `formula`, `type`, `default_value`, `unit`, `warning_lower_bound`, `warning_upper_bound`, `alarm_lower_bound`, `alarm_upper_bound`, `id` FROM `tbl_parameters` WHERE `id`=%s;"
        values = (id, )
        self.cursor.execute(query, values)
        temp = self.cursor.fetchone()
        if temp == None:
            return temp
        return Parameter(*temp)

    def get_current_value_of_parameter_by_variable_name(self, variable_name):
        query = "SELECT `id` FROM `tbl_parameters` WHERE `variable_name`=%s;"
        values = (variable_name, )
        self.cursor.execute(query, values)
        id = self.cursor.fetchone()[0]
        query = "SELECT `value` FROM `tbl_parameters_log` WHERE `parameter`=%s ORDER BY `date` DESC LIMIT 1;"
        values = (id, )
        self.cursor.execute(query, values)
        return self.cursor.fetchone()[0]

    def change_parts_order(self, id, order):
        query = "UPDATE `tbl_sections` SET `order` = %s WHERE (`id` = %s);"
        values=(order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def change_places_order(self, id, order):
        query = "UPDATE `tbl_places` SET `order` = %s WHERE (`id` = %s);"
        values=(order, id)
        self.cursor.execute(query, values)
        self.connection.commit()
        return ("ok", 0)

    def change_parameters_order(self, id, order):
        query = "UPDATE `tbl_parameters` SET `order` = %s WHERE (`id` = %s);"
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
        query = "SELECT `name`, `surname`, `username`, `password`, `access_level`, `wrong_times`, `default_date`, `id` FROM `tbl_users` where username=%s;"
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
        query = "SELECT `tbl_parameters`.`id`, `tbl_parameters`.`name`, `tbl_places`.`title`, `tbl_sections`.`title` FROM `tbl_parameters` join `tbl_sections` join `tbl_places` WHERE `tbl_parameters`.`section`=`tbl_sections`.`id` AND `tbl_parameters`.`place`=`tbl_places`.`id` ORDER BY `tbl_sections`.`order`, `tbl_places`.`order`, `tbl_parameters`.`order`;"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def set_min_date_into_temp_table(self, selected_date: datetime):
        # query = "TRUNCATE TABLE `tbl_parameters_min_date`;"
        # self.cursor.execute(query)
        # query = "INSERT INTO `tbl_parameters_min_date` SELECT NULL, `parameter_id`, MIN(`date`) FROM `tbl_parameters_log` WHERE `date`>%s GROUP BY `parameter_id`;"
        # values = (selected_date, )
        # self.cursor.execute(query, values)
        # self.connection.commit()

        # این بهینه تره ولی با احتمال خطا. چون فقط یک سال رو بررسی میکنه
        query = "TRUNCATE TABLE `tbl_parameters_min_date`;"
        self.cursor.execute(query)
        query = "INSERT INTO `tbl_parameters_min_date` SELECT NULL, `parameter_id`, MIN(`date`) FROM `tbl_parameters_log` WHERE `date`>%s AND `date`<=%s GROUP BY `parameter_id`;"
        try:
            next_year_date=selected_date.replace(year=selected_date.year+1)
        except ValueError: # ممکنه سال کبیسه باشه و روزی باشه که سال بعد اون رو نداره. در این صورت روز معادل سال بعد ارور میده. پس روزش رو یه دونه کم میکنیم تو این حالت
            next_year_date=selected_date.replace(year=selected_date.year+1, day=selected_date.day-1)
        values = (selected_date, next_year_date)
        self.cursor.execute(query, values)
        self.connection.commit()


    def set_max_date_into_temp_table(self, selected_date: datetime):
        # query = "TRUNCATE TABLE `tbl_parameters_max_date`;"
        # self.cursor.execute(query)
        # query = "INSERT INTO `tbl_parameters_max_date` SELECT NULL, `parameter_id`, MAX(`date`) FROM `tbl_parameters_log` WHERE `date`<=%s GROUP BY `parameter_id`;"
        # values = (selected_date, )
        # self.cursor.execute(query, values)
        # self.connection.commit()

        # این بهینه تره ولی با احتمال خطا. چون فقط یک سال رو بررسی میکنه
        query = "TRUNCATE TABLE `tbl_parameters_max_date`;"
        self.cursor.execute(query)
        query = "INSERT INTO `tbl_parameters_max_date` SELECT NULL, `parameter_id`, MAX(`date`) FROM `tbl_parameters_log` WHERE `date`<=%s AND `date`>%s GROUP BY `parameter_id`;"
        try:
            last_year_date=selected_date.replace(year=selected_date.year-1)
        except ValueError: # ممکنه سال کبیسه باشه و روزی باشه که سال قبل اون رو نداره. در این صورت روز معادل سال قبل ارور میده. پس روزش رو یه دونه کم میکنیم تو این حالت
            last_year_date=selected_date.replace(year=selected_date.year-1, day=selected_date.day-1)
        values = (selected_date, last_year_date)
        self.cursor.execute(query, values)
        self.connection.commit()

    def get_all_parameters_formula(self):
        query = "SELECT `formula` FROM `tbl_parameters`;"
        self.cursor.execute(query)
        formulas = []
        for formula in self.cursor.fetchall():
            formulas.append(formula[0])
        return formulas

if __name__ == "__main__":
    c = Connection()
