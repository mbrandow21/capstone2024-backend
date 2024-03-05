from flask import jsonify, request
from . import auth  # Import the Blueprint you defined in flaskr/auth/__init__.py
from .user_creation import create_user
from .user_verification import verify_user
from tokens import authenticateToken

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check if data exists and if it contains required fields
    if not data or 'username' not in data or 'password' not in data:
        print("error invalid request data")
        return jsonify({"error": "Invalid request data"}), 400

    username = data['username'].strip()
    password = data['password'].strip()

    if not username:
        print("Error: username not specified")
        return jsonify({"error": "Enter a username"}), 400
    if not password:
        print("Error: Password not specified")
        return jsonify({"error": "Enter a password"}), 400

    success = create_user(username, password)
    if success:
        print("Registration Successful")
        return jsonify({"message": "Registration successful!"}), 201
    else:
        print("Registration failed or username already exists")
        return jsonify({"error": "Registration failed or username already exists"}), 400

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(data)

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Invalid request data"}), 400

    username = data['username']
    password = data['password']

    response, status_code = verify_user(username, password)
    if status_code == 200:
        token = response
        print(token)
        return jsonify({"message": "Login successful!", "token": token}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401
    
@auth.route('/checkauth', methods=['POST'])
def checkauth():

    # data = request.get_json()

    # print(data)
    # every route has to return something! part of the error you were having is because the line below did not exist
    # return jsonify({"message": "success", "access_token": data}), 200


    # Extracting token from the 'Authorization' header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
    else:
        return jsonify({"error": "Bearer token not found"}), 401

    user_id, status_code = authenticateToken(token)
    if status_code == 200:
        return jsonify({"message": "Authentication Successful", "user_id": user_id, "authenticated": True}), 200
    else:
        return jsonify({"error": "Authentication Failed", "authenticated": False}), 401
