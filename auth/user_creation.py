import pyodbc
import bcrypt
from dbconnection import dbconnection


#This is a basic user creation that only works for administrators so far.
def create_user(username, password):
    connection_string = dbconnection()
    with pyodbc.connect(connection_string) as connection:
        with connection.cursor() as cursor:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            company_ID = 1
            try:
                cursor.execute("INSERT INTO Users (Username, Password, Company_ID) VALUES (?, ?, ?)", (username, hashed, company_ID))
                connection.commit()
                return True
            except pyodbc.IntegrityError:
                # Handle duplicate usernames
                return False
            except pyodbc.Error as e:
                # Handle other database errors
                print("Database error:", e)
                return False
