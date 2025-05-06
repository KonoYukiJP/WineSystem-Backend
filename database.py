# database.py

import mysql.connector

class DatabaseError(Exception):
    pass

def connect():
    try:
        return mysql.connector.connect(
            host='163.43.218.237',
            user='flask_user',
            password='P@ssw0rd',
            database='wine_database'
        )
    except mysql.connector.Error as error:
        raise DatabaseError(f"Database connection error: {error}")
