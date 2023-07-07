import sqlite3

__all__ = ['db']


class Database:
    def __init__(self, file_path):
        self._connect = sqlite3.connect(file_path)
        self._cursor = self._connect.cursor()
        self.__init()

    def __init(self):
        cursor = self._cursor
        cursor.execute("""CREATE TABLE IF NOT EXISTS monitoring_chats (
                chat_id TEXT NOT NULL
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT NOT NULL
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS stop_words (
                word TEXT NOT NULL
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS key_words (
                word TEXT NOT NULL
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS black_list (
                user_id TEXT NOT NULL
        )""")
        self._connect.commit()

    def create(self, table, value):
        self._cursor.execute(f"INSERT INTO {table} VALUES ('{value}')")
        self._connect.commit()
    
    def get_all(self, table):
        self._cursor.execute(f'SELECT * FROM {table}')
        return self._cursor.fetchall()
    
    def delete(self, table, attr, value):
        self._cursor.execute(f"DELETE FROM {table} WHERE {attr} = '{value}'")
        self._connect.commit()


db = Database('db.db')
