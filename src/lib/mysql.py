import os

import mysql.connector


class MySQLClient(object):
    def __init__(self,
                 host: str = 'localhost',
                 port: int = 3306,
                 user: str = 'root',
                 password: str = None,
                 database: str = None,
                 charset: str = 'utf8mb4') -> None:
        self.conf = dict(
            host=host,
            port=port,
            user=user,
            password=password or os.getenv('MYSQL_PASSWORD'),
            database=database,
            charset=charset
        )

    def execute(self,
                operation: str,
                autocommit: bool = False,
                dictionary: bool = True) -> list:
        conn = mysql.connector.connect(**self.conf)
        conn.autocommit = autocommit

        result = []
        with conn.cursor(dictionary=dictionary) as cursor:
            try:
                cursor.execute(operation)
                result.extend(cursor.fetchall())
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

        return result

    def executemany(self,
                    operation: str,
                    data: list,
                    autocommit: bool = False,
                    dictionary: bool = True) -> None:
        conn = mysql.connector.connect(**self.conf)
        conn.autocommit = autocommit

        with conn.cursor(dictionary=dictionary) as cursor:
            try:
                cursor.executemany(operation, data)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
