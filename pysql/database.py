import mysql.connector
from .settings import DB_NAME, HOST, USER, PASSWORD


class Database:
    def __init__(self):
        self.__db = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD
        )

        self.__cursor = self.__db.cursor()
        self.__create_database()

    def clear(self):
        self.execute("DROP DATABASE " + DB_NAME + ";")
        self.__create_database()

    def __create_database(self):
        self.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        self.execute(f"USE {DB_NAME}")
        self.execute("CREATE TABLE IF NOT EXISTS Log(id INT AUTO_INCREMENT PRIMARY KEY,log TEXT);")
        self.execute("""
            CREATE PROCEDURE IF NOT EXISTS get_tables(IN name_starts_with VARCHAR(10))
            BEGIN 
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME LIKE CONCAT(name_starts_with,'%');
            END
        """)
        self.close()

        self.__db = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB_NAME
        )

        self.__cursor = self.__db.cursor()

    def get_table_names(self, starts_with):
        result = self.execute(f"CALL get_tables('{starts_with}');")
        return result

    def close(self):
        self.__db.commit()
        self.__cursor.close()
        self.__db.close()

    def create_object(self, query):
        self.__cursor.execute(query)
        return self.__cursor.lastrowid

    def execute(self, query):
        self.__cursor.execute(query)
        return list(self.__cursor)
