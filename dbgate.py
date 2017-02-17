import mysql.connector

class MysqlConnector(object):
    def __init__(self, host, port, user, password, database):
        print('connect to ', host)
        self.cnx = mysql.connector.connect(user=user,
                                           password=password,
                                           host=host,
                                           port=port,
                                           database=database)
        self.cursor = self .cnx.cursor()

    def __enter__(self):
        return self.cursor

    def __exit__(self, ext_type, exc_value, traceback):
        self.commit()
        self.cursor.close()
        self.cnx.close()

    def __iter__(self):
        for item in self.cursor:
            yield item

    def commit(self):
        self.cnx.commit()

add_following = ("INSERT INTO following "
                 "(name, gender, nick, home_page, portrait) "
                 "VALUES (%s, %s, %s, %s, %s)")

data = ('li-ming', 'M', '小明明', 'https://www.baidu.com', 'https://www.google.com')

with MysqlConnector('172.25.51.7', 6606, 'root', '123456', 'zhihu') as h:
    h.execute(add_following, data)