from flask import Blueprint,request,jsonify
from database import connect

from . import systems_bp

def fetch_table(query, params = ()):
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    cursor.execute(query, params)
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result
    
@systems_bp.route('/<int:system_id>/roles', methods = ['GET'])
def fetch_roles_in_system(system_id):
    try:
        query = '''
            SELECT role.id, role.name
            FROM roles role
            WHERE role.system_id = %s
        '''
        params = (system_id, )
        roles = fetch_table(query, params)
        
        connection = connect()
        cursor = connection.cursor(dictionary = True)
        
        for role in roles:
            cursor.execute('''
                    SELECT permission.action_id, permission.resource_id
                    FROM permissions permission
                    WHERE permission.role_id = %s
                ''', (role['id'],))
            role['permissions'] = cursor.fetchall()
        
        return jsonify(roles), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@systems_bp.route('/<int:system_id>/roles', methods = ['POST'])
def insert_role_in_system(system_id):
    body = request.get_json()
    name = body.get('name')

    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM systems WHERE id = %s)', (system_id,))
        system_exists = cursor.fetchone()[0]
        if not system_exists:
            return jsonify({"message": "System Not Found."}), 404
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM roles WHERE name = %s AND system_id = %s)', (name, system_id))
        role_exists = cursor.fetchone()[0]
        if role_exists:
            return jsonify({"message": "Role with this name already exists."}), 401
        
        cursor.execute('INSERT INTO roles (system_id, name) VALUES (%s, %s)', (system_id, name))
        connection.commit()
        return jsonify({"message": "Role was inserted successly"}), 201
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


