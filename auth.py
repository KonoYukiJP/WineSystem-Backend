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
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours = 12)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm = 'HS256')

def check_permission(user_id, resource, action):
    try:
        with connect() as connection:
            with connection.cursor(dictionary = True) as cursor:
                query = 'SELECT role_id FROM users WHERE id = %s'
                params = (user_id, )
                cursor.execute(query, params)
                user = cursor.fetchone()
                if not user:
                    return False, 'User Not Found'
                role_id = user['role_id']
                
                query = '''
                    SELECT EXISTS (
                        SELECT 1 
                        FROM permissions p
                        JOIN resources r ON r.id = p.resource_id
                        JOIN actions a ON a.id = p.action_id
                        WHERE p.role_id = %s AND r.name = %s AND a.name = %s
                    ) AS permission
                '''
                params = (role_id, resource, action)
                cursor.execute(query, params)
                if not cursor.fetchone()['permission']:
                    return False, 'Permission denied'
        return True, None
    except Exception as e:
        return False, str(e)

def authorization_required(resource = None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1]
            else:
                return jsonify({'message': 'Token is missing!'}), 401
            try:
                data = jwt.decode(token, SECRET_KEY, algorithms = ['HS256'])
                request.user = {'id': data['user_id']}
            except Exception:
                return jsonify({'message': 'Token is invalid!'}), 401
                
            if resource:
                if request.method in ('PUT', 'PATCH'):
                    action = 'Update'
                else:
                    action = request.method
                ok, e = check_permission(request.user['user_id'], resource, action)
                if not ok:
                    return jsonify({'message': e}), 403 if e == 'Permission denied' else 500

            return f(*args, **kwargs)
        return wrapper
    return decorator
