from flask import request, jsonify, Response
from . import api  # Import the Blueprint you defined in flaskr/auth/__init__.py
from flask import Flask, request
from tokens import authenticateToken
import pyodbc
from dbconnection import dbconnection
import base64
import json
from .functions import custom_serializer

@api.route('/sendgrid/updatemessages/f829fca9-1e0f-4e06-a67f-20a0b2a025ca', methods=['POST'])
def get_sendgrid_webhook ():
    headers=request.headers
    print("RECIEVED WEBHOOK, SENDING HEADERS",headers)

    data = request.json

    print("THIS IS THE DATA", data)
    return jsonify({"message": "Data successfully Recieved"})




@api.route('/post/procedure', methods=['POST'])
def run_procedure():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Bearer token not found"}), 401
    token = auth_header.split(" ")[1]

    user_id, status_code = authenticateToken(token)
    if status_code != 200:
        return jsonify({"error": "Authentication failed"}), status_code

    procName = request.args.get('proc')
    parameters = request.args.get('parameters', None)

    print('THIS IS PARAMETERS', parameters)


    try:
        parameters_dict = json.loads(parameters) if parameters else {}
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format for parameters"}), 400

    connection_string = dbconnection()
    # Assuming dbconnection() returns a valid connection string

    try:
        with pyodbc.connect(connection_string) as connection:
            with connection.cursor() as cursor:
                # Prepare and execute the stored procedure with parameters
                params = [user_id] + list(parameters_dict.values())
                sql = f"EXEC {procName} ? " + " ".join([",?"] * len(parameters_dict))
                print('HERE IS MY SQL', sql)
                cursor.execute(sql, params)

                all_result_sets = []
                while True:  # Start a loop that will run at least once
                    if cursor.description is not None:  # Ensure there are results to fetch
                        columns = [column[0] for column in cursor.description]
                        rows = cursor.fetchall()
                        if rows:
                            data = [dict(zip(columns, row)) for row in rows]
                            # Handle bytes data within the current result set
                            for item in data:
                                for key, value in item.items():
                                    if isinstance(value, bytes):
                                        item[key] = base64.b64encode(value).decode('utf-8')
                            all_result_sets.append(data)
                    if not cursor.nextset():  # Check if there are more result sets
                        break  # Exit the loop if no more result sets are available

                # Convert all_result_sets to JSON string with order preserved
                json_data = json.dumps(all_result_sets, default=custom_serializer, sort_keys=False)

                
                # Return JSON string with MIME type as application/json
                return Response(json_data, mimetype='application/json') if all_result_sets else jsonify({"error": "No data found, but stored procedure was executed."})
    except pyodbc.Error as e:
        print(e)
        return jsonify({"error": "Server error"}), 500

@api.route('/get', methods=['GET'])
def get_data():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"error": "Bearer token not found"}), 401

    user_id, status_code = authenticateToken(token)

    if status_code != 200:
        return jsonify({"error": "Authentication failed"}), status_code

    tableName = request.args.get('from')
    select = request.args.get('select', '*')  # Defaults to '*' if 'select' is not provided
    filter = request.args.get('filter', 'none')
    join = request.args.get('join', '')

    if filter != 'none':
        filter = ' WHERE ' + filter
    # print(tableName)
    # Validate tableName and select here


    connection_string = dbconnection()
    from flask import jsonify

# Inside your endpoint function, after fetching data with cursor.fetchall()
    try:
        with pyodbc.connect(connection_string) as connection:
            with connection.cursor() as cursor:
                print("EXEC api_GetProcedure ?, ?, ?, ?, ?", user_id, tableName, select, filter, join)
                cursor.execute("EXEC api_GetProcedure ?, ?, ?, ?, ?", user_id, tableName, select, filter, join)
                rows = cursor.fetchall()
                
                # Convert rows to a list of dicts and preserve order
                columns = [column[0] for column in cursor.description]
                data = [dict(zip(columns, row)) for row in rows]

                # Handle bytes data and preserve order
                for item in data:
                    for key, value in item.items():
                        if isinstance(value, bytes):
                            item[key] = base64.b64encode(value).decode('utf-8')  # Convert bytes to Base64 encoded string

                # Convert data to JSON string with order preserved
                json_data = json.dumps(data, sort_keys=False)
                
                # Return JSON string with MIME type as application/json
                return Response(json_data, mimetype='application/json') if data else jsonify({"error": "No data found"})
    except pyodbc.Error as e:
        # Log the error
        print(e)
        return jsonify({"error": "Server error"}), 500


@api.route('/post/createrecord', methods=['POST'])
def createRecord():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"error": "Bearer token not found"}), 401

    user_id, status_code = authenticateToken(token)

    if status_code != 200:
        return jsonify({"error": "Authentication failed"}), status_code

    data = request.get_json()  # This method parses the JSON data
    data_dict = data['recordData']
    table_name = data['tablename']
    # Generate column names and placeholders for values
    columns = ', '.join(data_dict.keys())
    placeholders = ', '.join(['?'] * len(data_dict))

    # Prepare the INSERT statement
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Values to be inserted
    values = tuple(data_dict.values())

    # Get a cursor from the connection
    connection_string = dbconnection()

    print(sql, values)

    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            try:
                # Execute the INSERT statement using a cursor
                cursor.execute(sql, values)
                # Commit the transaction
                conn.commit()
                print("Record inserted successfully.")
                return jsonify({"data": "Record Inserted Successfully"}), 200
            except Exception as e:
                print(f"An error occurred: {e}")
                # Roll back if there's an error
                conn.rollback()
                # It's better to return a generic error message to the client
                return jsonify({"error": "An error occurred during record insertion"}), 500
    except pyodbc.Error as e:
        # Log the error
        print(e)
        return jsonify({"error": "Server error"}), 500


@api.route('/post/updateRecord', methods=['POST'])
def updateRecord():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"error": "Bearer token not found"}), 401

    user_id, status_code = authenticateToken(token)

    if status_code != 200:
        return jsonify({"error": "Authentication failed"}), status_code

    data = request.get_json()  # This method parses the JSON data
    recordId = data['recordId']
    tableId = data['tableId']
    data_dict = data['recordData']
    # Generate column names and placeholders for values

    formatted_string = str(', '.join([f"{key}='{value}'" if isinstance(value, str) else f"{key}={value}" for key, value in data_dict.items()]))

    # Prepare the INSERT statement
    sql = f"EXEC [db_apiUpdateRecord] @UserID = ?, @UpdateStuff = ?, @TableID = ?, @RecordID = ?"

    # # Values to be inserted
    # values = tuple(data_dict.values())

    # # Get a cursor from the connection
    connection_string = dbconnection()

    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            try:
                # Execute the INSERT statement using a cursor
                cursor.execute(sql, user_id, formatted_string, tableId, recordId)
                # Commit the transaction
                conn.commit()
                print("Data Sent.")
                return jsonify({"data": "Record Updated Successfully"}), 200
            except Exception as e:
                print(f"An error occurred: {e}")
                # Roll back if there's an error
                conn.rollback()
                # It's better to return a generic error message to the client
                return jsonify({"error": "An error occurred during record insertion"}), 500
    except pyodbc.Error as e:
        # Log the error
        print(e)
        return jsonify({"error": "Server error"}), 500
    

@api.route('/delete/deleteRecord', methods=['DELETE'])
def deleteRecord():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"error": "Bearer token not found"}), 401

    user_id, status_code = authenticateToken(token)

    if status_code != 200:
        return jsonify({"error": "Authentication failed"}), status_code
    
    tableID = request.args.get('tableID')
    recordID = request.args.get('recordID')

    print('THIS IS WHAT IM DELETING', tableID, recordID)

    sql = f"EXEC api_db_deleteRecord @UserID=?, @PageID=?, @RecordID=?"

    connection_string = dbconnection()

    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            try:
                # Execute the INSERT statement using a cursor
                cursor.execute(sql, user_id, tableID, recordID)
                # Commit the transaction
                conn.commit()
                return jsonify({"data": "Record Deleted Successfully"}), 200
            except Exception as e:
                print(f"An error occurred: {e}")
                # Roll back if there's an error
                conn.rollback()
                # It's better to return a generic error message to the client
                return jsonify({"error": "An error occurred during record insertion"}), 500
    except pyodbc.Error as e:
        # Log the error
        print(e)
        return jsonify({"error": "Server error"}), 500