# users.py

from flask import Blueprint, request, jsonify
import bcrypt

from auth import authorization_required
from database import connect, fetchall

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods = ['GET'])
@authorization_required('User')
def get_users_in_system():
    system_id = request.user['system_id']
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

@users_bp.route('', methods = ['POST'])
@authorization_required('User')
def create_user_in_system():
    system_id = request.user['system_id']
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

@users_bp.route('/me/name', methods = ['GET'])
@authorization_required()
def get_username_in_users():
    query = 'SELECT name FROM users AS user WHERE user.id = %s'
    params = (request.user['id'], )
    user = fetchall(query, params)[0]
    return jsonify(user['name']), 200

@users_bp.route('/<int:user_id>', methods = ['PUT'])
@authorization_required('User')
def update_user(user_id):
    body = request.get_json()

    try:
        username = body['name']
        role_id = body['role_id']
        is_enabled = body['is_enabled']
    except KeyError:
        return jsonify({'message': 'Invalid request format'}), 400
    
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'UPDATE users SET name = %s, role_id = %s, is_enabled = %s WHERE id = %s'
            params = (username, role_id, is_enabled, user_id)
            cursor.execute(query, params)
            connection.commit()
        
        return jsonify({"message": "User was updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@users_bp.route('/me/name', methods = ['PUT'])
@authorization_required()
def update_username():
    body = request.get_json()
    user_id = request.user['id']
    
    try:
        username = body.get('name')
    except KeyError:
        return jsonify({'message': 'Invalid request format'}), 400
    
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'UPDATE users SET name = %s WHERE id = %s'
            params = (username, user_id)
            cursor.execute(query, params)
            connection.commit()
        
        return jsonify({"message": "User was updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@users_bp.route('/me/password', methods=['PUT'])
@authorization_required()
def update_password_in_user():
    body = request.get_json()
    user_id = request.user['id']
    
    try:
        old_password = body['old_password']
        new_password = body['new_password']
    except KeyError:
        return jsonify({'message': 'Invalid request format'}), 400
    
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'SELECT user.password_hash FROM users AS user WHERE user.id = %s'
            params = (user_id, )
            cursor.execute(query, params)
            password_hash = cursor.fetchone()[0]
            if not password_hash:
                return jsonify({"message": "User Not Found"}), 404
            
            if not bcrypt.checkpw(
                old_password.encode('utf-8'),
                password_hash.encode('utf-8')
            ):
                return jsonify({"message": "Invalid current password"}), 400
            
            # 新しいパスワードをハッシュ化して保存
            new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            query = 'UPDATE users SET password_hash = %s WHERE id = %s'
            params = (new_password_hash, user_id)
            cursor.execute(query, params)
            connection.commit()
        
        return jsonify({"message": "Password was changed successfully."}), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500

@users_bp.route('/<int:user_id>', methods = ['DELETE'])
@authorization_required('User')
def delete_user(user_id):
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id, ))
            connection.commit()

        return jsonify({"message": "System deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
