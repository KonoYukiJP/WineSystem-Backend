# systems.py

import os

from flask import Blueprint, request, jsonify
import bcrypt

from auth import generate_token
from database import connect, fetchall

systems_bp = Blueprint('systems', __name__)

@systems_bp.route('', methods = ['GET'])
def get_systems():
    systems = fetchall('SELECT id, name, year, admin_name, password FROM systems')
    return jsonify(systems)
    
@systems_bp.route('/<int:system_id>', methods = ['GET'])
def fetch_system(system_id):
    query = 'SELECT id, name, year FROM systems AS `system` WHERE `system`.id = %s'
    system = fetchall(query, (system_id, ))[0]
    return jsonify(system), 200

@systems_bp.route('', methods = ['POST'])
def create_system():
    body = request.get_json()
    
    try:
        name = body['name']
        year = body['year']
        owner_name = body['owner_name']
        password = body['password']
    except KeyError:
        return jsonify({'message': 'Invalid request format'}), 400
    
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            cursor.execute("SELECT EXISTS (SELECT 1 FROM systems WHERE name = %s)", (name, ))
            system_exists = cursor.fetchone()[0]
            
            if system_exists:
                return jsonify({"message": "System name already exists."}), 400
                
            
            cursor.execute(
                '''
                    INSERT INTO systems (name, year, admin_name, password) 
                    VALUES (%s, %s, %s, %s)
                ''',
                (name, year, owner_name, password)
            )
            system_id = cursor.lastrowid
            
            cursor.execute(
                'INSERT INTO roles (system_id, name) VALUES (%s, %s)',
                (system_id, "Owner")
            )
            role_id = cursor.lastrowid
            resources = fetchall('SELECT id FROM resources')
            actions = fetchall('SELECT id FROM actions')
            for resource in resources:
                for action in actions:
                    cursor.execute(
                        '''
                        INSERT INTO permissions (role_id, resource_id, action_id)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE role_id = role_id
                        ''',
                        (role_id, resource['id'], action['id'])
                    )
            
            cursor.execute(
                'INSERT INTO users (system_id, name, password_hash, role_id, is_enabled)VALUES (%s, %s, %s, %s, %s)',
                (system_id, owner_name, password_hash, role_id, '1')
            )
            cursor.execute(
                'INSERT INTO roles (system_id, name) VALUES (%s, %s)',
                (system_id, "Member")
            )
            connection.commit()
            backup_dir = os.path.join('backups', f'system_{system_id}')
            os.makedirs(backup_dir, exist_ok = True)
        return jsonify({"message": "System was created successly."}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@systems_bp.route('/<int:system_id>', methods=['PATCH'])
def update_system(system_id):
    body = request.get_json()
    system_name = body.get('name')
    system_year = body.get('year')
    
    try:
        connection = connect()
        cursor = connection.cursor()
        
        if system_name is not None:
            cursor.execute('SELECT EXISTS(SELECT 1 FROM systems AS `system` WHERE system.name = %s)', (system_name, ))
            result = cursor.fetchone()
            if result[0]:
                return jsonify({"message": "System name already exists."}), 404
            
            cursor.execute(
                'UPDATE systems SET name = %s WHERE id = %s',
                (system_name, system_id)
            )
            
        if system_year is not None:
            cursor.execute(
                'UPDATE systems SET year = %s WHERE id = %s',
                (system_year, system_id)
            )
            
        connection.commit()
        
        return jsonify({"message": "Password was changed successfully."}), 200
    except Exception as error:
        print(str(error))
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@systems_bp.route('/<int:system_id>', methods = ['DELETE'])
def delete_system(system_id):
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            cursor.execute('SELECT EXISTS (SELECT 1 FROM systems WHERE id = %s)', (system_id,))
            result = cursor.fetchone()
            if not result[0]:
                return jsonify({"message": "Not Found"}), 404
            
            cursor.execute('DELETE FROM users WHERE system_id = %s', (system_id, ))

            cursor.execute('DELETE FROM systems WHERE id = %s', (system_id,))
            connection.commit()
        
        return jsonify({"message": "System deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

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
        return jsonify(token)
    except Exception as e:
        return jsonify({'message': str(e)}), 500
