# login.py

import datetime

from flask import Blueprint, request, jsonify
import bcrypt

from . import systems_bp
from auth import generate_token
from database import connect

@systems_bp.route('/<int:system_id>/login', methods = ['POST'])
def login(system_id):
    body = request.get_json()
    
    try:
        username = body['username']
        password = body['password']
    except KeyError:
        return jsonify({'message': 'Invalid request format'}), 400
        
    query = '''
        SELECT user.id, user.password_hash
        FROM users user
        JOIN systems `system` ON `system`.id = user.system_id
        WHERE `system`.id = %s AND user.name = %s
    '''
    params = (system_id, username)
    try:
        with (
            connect() as connection,
            connection.cursor(dictionary = True) as cursor
        ):
            cursor.execute(query, params)
            user = cursor.fetchone()
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
    if not user:
        return jsonify({'message': 'User Not Found'}), 404
        
    if not bcrypt.checkpw(
        password.encode('utf-8'),
        user['password_hash'].encode('utf-8')
    ):
        return jsonify({'message': 'Invalid user or password'}), 401
        
    try:
        token = generate_token(user['id'])
        return jsonify({'token': token})
    except Exception as e:
        return jsonify({'message': str(e)}), 500
