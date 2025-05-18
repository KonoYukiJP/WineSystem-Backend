# users.py

from flask import Blueprint,request,jsonify
import bcrypt

from . import systems_bp
from auth import authorization_required
from database import connect, fetchall

@systems_bp.route('/<int:system_id>/users', methods = ['GET'])
def get_users_in_system(system_id):
    try:
        query = '''
            SELECT user.id, user.name, role_id, user.is_enabled
            FROM users user
            WHERE user.system_id = %s
        '''
        params = (system_id, )
        results = fetchall(query, params)
        for user in results:
            user['is_enabled'] = bool(user['is_enabled'])
        return jsonify(results), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500

@systems_bp.route('/<int:system_id>/users', methods = ['POST'])
@authorization_required('User')
def create_user_in_system(system_id):
    body = request.get_json()
    try:
        user_name = body['name']
        password = body['password']
        role_id = body['role_id']
        is_enabled = body['is_enabled']
    except KeyError:
        return jsonify({'message': 'Invalid request format'}), 400
        
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'SELECT EXISTS (SELECT 1 FROM systems WHERE id = %s)'
            params = (system_id, )
            cursor.execute(query, params)
            system_exists = cursor.fetchone()[0]
            if not system_exists:
                return jsonify({"message": "System Not Found."}), 404
            
            query = 'SELECT EXISTS (SELECT 1 FROM users WHERE system_id = %s AND name = %s)'
            params = (system_id, user_name)
            cursor.execute(query, params)
            name_exists = cursor.fetchone()[0]
            if name_exists:
                return jsonify({"message": "This name is already taken."}), 409
            
            query = '''
                INSERT INTO users (system_id, name, password_hash, role_id, is_enabled)
                VALUES (%s, %s, %s, %s, %s)
            '''
            params = (system_id, user_name, password_hash, role_id, is_enabled)
            cursor.execute(query, params)
            connection.commit()
            
        return jsonify({'message': 'Success'}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
