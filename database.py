import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host="localhost", user="root", password="shriram2003", database="telecom_tracker"):
        """Initialize the database connection"""
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            self.cursor = self.conn.cursor()
            
            # Creating database if it doesn't exist
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
            self.cursor.execute(f"USE {database}")
            
            print("Connected to database successfully!")
        except Error as err:
            print(f"Error connecting to MySQL: {err}")
            exit(1)
    
    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        except Error as err:
            print(f"Error executing query: {err}")
            return None
    
    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return []
    
    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None
    
    def commit(self):
        """Commit changes to database"""
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("Database connection closed.")