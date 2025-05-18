# database.py

import mysql.connector

def connect():
    return mysql.connector.connect(
        host = '163.43.218.237',
        user = 'flask_user',
        password = 'P@ssw0rd',
        database = 'wine_database'
    )

def fetchall(query, params = ()):
    with (
        connect() as connection,
        connection.cursor(dictionary = True) as cursor
    ):
        cursor.execute(query, params)
        result = cursor.fetchall()
    return result

