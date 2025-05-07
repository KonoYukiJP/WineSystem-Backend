from flask import Blueprint,request,jsonify
from database import connect
import bcrypt

from . import systems_bp

def fetch_table(query, params = ()):
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    cursor.execute(query, params)
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

@systems_bp.route('/<int:system_id>/users', methods = ['GET'])
def fetch_users_in_system(system_id):
    try:
        query = '''
            SELECT user.id, user.name, role_id, user.is_enabled
            FROM users user
            WHERE user.system_id = %s
        '''
        params = (system_id, )
        results = fetch_table(query, params)
        for user in results:
            user['is_enabled'] = bool(user['is_enabled'])
        return jsonify(results), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500

@systems_bp.route('/<int:system_id>/users', methods = ['POST'])
def insert_user_in_system(system_id):
    body = request.get_json()
    user_name = body.get('name')
    password = body.get('password')
    role_id = body.get('role_id')
    is_enabled = body.get('is_enabled')
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM systems WHERE id = %s)', (system_id, ))
        system_exists = cursor.fetchone()[0]
        if not system_exists:
            return jsonify({"message": "System Not Found."}), 404
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM users WHERE system_id = %s AND name = %s)', (system_id, user_name))
        user_exists = cursor.fetchone()[0]
        if user_exists:
            return jsonify({"message": "User with this name already exists."}), 401
        
        cursor.execute('''
                INSERT INTO users (system_id, name, password_hash, role_id, is_enabled)
                VALUES (%s, %s, %s, %s, %s)
            ''',
            (system_id, user_name, password_hash, role_id, is_enabled)
        )
        connection.commit()
        return jsonify({"message": "User was created successly"}), 201
        
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
