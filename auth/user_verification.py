from flask import jsonify
import pyodbc
import bcrypt
from dbconnection import dbconnection
from tokens import assign_token

def verify_user(username, password):
    connection_string = dbconnection()
    with pyodbc.connect(connection_string) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT U.Password, U.User_ID, U.Verified FROM Users U WHERE U.Username=?", (username,))
            row = cursor.fetchone()
            
            if not row:
                return {"error": "Invalid email"}, 401

            verified, user_ID, stored_hashed_password = row[2], row[1], row[0].decode('utf-8')

            if not verified:
                return {"error": "User is not verified"}, 401

            if not bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                return {"error": "Invalid password"}, 401

            response, status_code = assign_token(user_ID, username)
            return (response, status_code)