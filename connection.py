import pymysql

class Connection():
    def __init__(self, host='127.0.0.1', user='root', password='root'):
        self.host = host
        self.user = user
        self.password = password
        self.connection = pymysql.connect(host=self.host, user=self.user, passwd=self.password, charset='utf8')
        self.cursor = self.connection.cursor()
        query = "CREATE SCHEMA IF NOT EXISTS `qaenpower`;"
        self.cursor.execute(query)
        query = "CREATE TABLE IF NOT EXISTS `qaenpower`.`users` (`id` INT UNSIGNED NOT NULL AUTO_INCREMENT, `name` VARCHAR(63) NOT NULL, `surname` VARCHAR(63) NOT NULL, `username` VARCHAR(63) NOT NULL, `password` VARCHAR(127) NOT NULL, PRIMARY KEY (`id`), UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE, UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);"
        self.cursor.execute(query)

    def create_user(self):
        pass

    def insert_counter(self):
        pass

    def update_counter(self):
        pass

c = Connection()
