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


@systems_bp.route('', methods = ['GET'], strict_slashes = False)
def fetch_systems():
    systems = fetch_table('SELECT id, name, year, admin_name, password FROM systems')
    return jsonify(systems)
    
@systems_bp.route('/<int:system_id>', methods = ['GET'])
def fetch_system(system_id):
    query = 'SELECT id, name, year FROM systems AS `system` WHERE `system`.id = %s'
    return fetch_table(query, (system_id, ))[0]

@systems_bp.route('', methods = ['POST'])
def insert_system():
    body = request.get_json()
    name = body.get('name')
    year = body.get('year')
    owner_name = body.get('owner_name')
    password = body.get('password')
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute("SELECT EXISTS(SELECT 1 FROM systems WHERE name = %s)", (name,))
        result = cursor.fetchone()
        system_exists = result[0]
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
        cursor.execute(
            'INSERT INTO users (system_id, name, password_hash, role_id, is_enabled)VALUES (%s, %s, %s, %s, %s)',
            (system_id, owner_name, password_hash, role_id, '1')
        )
        cursor.execute(
            'INSERT INTO roles (system_id, name) VALUES (%s, %s)',
            (system_id, "Member")
        )
        connection.commit()
        return jsonify({"message": "System was created successly."}), 201
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

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
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM systems WHERE id = %s)', (system_id,))
        result = cursor.fetchone()
        if not result[0]:
            return jsonify({"message": "Not Found"}), 404

        cursor.execute('DELETE FROM users WHERE system_id = %s', (system_id, ))

        # アイテムを削除
        cursor.execute('DELETE FROM systems WHERE id = %s', (system_id,))
        connection.commit()
        
        return jsonify({"message": "System deleted successfully"}), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
