# login.py

from flask import Blueprint, request, jsonify
from database import connect
import bcrypt

login_bp = Blueprint('login', __name__)

def fetch_table(query, params = ()):
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    cursor.execute(query, params)
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


@login_bp.route('', methods=['POST'])
def login():
    try:
        body = request.get_json()
        system_id = body.get('systemId')
        user_id = body.get('userId')
        password = body.get('password')
        print(system_id, user_id, password)
        user = fetch_table('''
            SELECT user.password_hash
            FROM users user
            JOIN systems `system` ON `system`.id = user.system_id
            WHERE `system`.id = %s AND user.id = %s
            ''', (system_id, user_id))[0]
        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return jsonify({"message": "Login successful"})
            else:
                return jsonify({"message": "Invalid credentials"}), 401
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as error:
        return jsonify({"message": str(error)}), 500
