from flask import Blueprint, request, jsonify
import bcrypt

from database import connect, fetchall

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>/name', methods = ['GET'])
def fetch_name_in_users(user_id):
    query = 'SELECT name AS value FROM users AS user WHERE user.id = %s'
    return fetchall(query, (user_id, ))[0]

@users_bp.route('/<int:user_id>', methods = ['PUT'])
def update_user(user_id):
    body = request.get_json()
    username = body.get('name')
    role_id = body.get('role_id')
    is_enabled = body.get('is_enabled')
    
    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute(
            'UPDATE users SET name = %s, role_id = %s, is_enabled = %s WHERE id = %s',
            (username, role_id, is_enabled, user_id)
        )
        connection.commit()
        
        return jsonify({"message": "User was updated successfully"}), 200
        
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@users_bp.route('/<int:user_id>/name', methods = ['PUT'])
def update_username(user_id):
    body = request.get_json()
    username = body.get('name')
    
    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute(
            'UPDATE users SET name = %s WHERE id = %s',
            (username, user_id)
        )
        connection.commit()
        
        return jsonify({"message": "User was updated successfully"}), 200
        
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@users_bp.route('/<int:user_id>/password', methods=['PUT'])
def update_password_in_user(user_id):
    body = request.get_json()
    old_password = body.get('old_password')
    new_password = body.get('new_password')
    
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # システム名とユーザー名でユーザーIDを取得
        cursor.execute(
            'SELECT user.password_hash FROM users AS user WHERE user.id = %s',
            (user_id, )
        )
        
        result = cursor.fetchone()
        if not result[0]:
            return jsonify({"message": "User not found"}), 404
        
        stored_password_hash = result[0]
        
        # 現在のパスワードが正しいかを確認
        if not bcrypt.checkpw(old_password.encode('utf-8'), stored_password_hash.encode('utf-8')):
            return jsonify({"message": "Invalid current password"}), 400
        
        # 新しいパスワードをハッシュ化して保存
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (new_password_hash, user_id))
        connection.commit()
        
        return jsonify({"message": "Password was changed successfully."}), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@users_bp.route('/<int:user_id>', methods = ['DELETE'])
def delete_user(user_id):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        connection.commit()

        return jsonify({"message": "System deleted successfully"}), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
