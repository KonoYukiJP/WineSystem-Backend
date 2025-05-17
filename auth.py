# auth.py

from functools import wraps
import datetime

from database import connect
from flask import request, jsonify
import jwt

SECRET_KEY = 'WineSystem'

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def authorization_required(resource):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # --- Tokenの検証 ---
            token = None
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1]  # "Bearer xxxx"

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                request.user = {'user_id': data['user_id']}
            except Exception as e:
                return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401

            user_id = request.user['user_id']

            # --- ロール取得 ---
            try:
                with connect() as connection:
                    with connection.cursor(dictionary=True) as cursor:
                        cursor.execute('SELECT role_id FROM users WHERE id = %s', (user_id,))
                        user = cursor.fetchone()
                        if not user:
                            return jsonify({'message': 'User Not Found'}), 404
                        role_id = user['role_id']
            except Exception as e:
                return jsonify({'message': str(e)}), 500

            # --- パーミッションチェック ---
            try:
                with connect() as connection:
                    with connection.cursor(dictionary=True) as cursor:
                        cursor.execute(
                            '''
                            SELECT EXISTS (
                                SELECT 1 
                                FROM permissions p
                                JOIN resources r ON r.id = p.resource_id
                                JOIN actions a ON a.id = p.action_id
                                WHERE p.role_id = %s AND r.name = %s AND a.name = %s
                            ) AS permission
                            ''',
                            (role_id, resource, request.method)
                        )
                        if not cursor.fetchone()['permission']:
                            return jsonify({'message': 'Permission denied'}), 403
            except Exception as e:
                return jsonify({'message': str(e)}), 500

            return f(*args, **kwargs)
        return wrapper
    return decorator
