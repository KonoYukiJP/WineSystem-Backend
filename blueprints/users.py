from flask import Blueprint, request, jsonify
import bcrypt

from auth import authorization_required
from database import connect, fetchall

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>/name', methods = ['GET'])
def get_username_in_users(user_id):
    query = 'SELECT name AS value FROM users AS user WHERE user.id = %s'
    params = (user_id, )
    user = fetchall(query, params)
    return jsonify(user[name]), 200

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

@users_bp.route('/<int:user_id>/name', methods = ['PUT'])
@authorization_required('User')
def update_username(user_id):
    body = request.get_json()
    
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

@users_bp.route('/<int:user_id>/password', methods=['PUT'])
def update_password_in_user(user_id):
    body = request.get_json()
    
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
