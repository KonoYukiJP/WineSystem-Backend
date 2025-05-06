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



@systems_bp.route('/<int:system_id>/materials', methods = ['GET'])
def fetch_materials_in_system(system_id):
    query = '''
        SELECT material.id, material.name, material.note
        FROM materials material
        WHERE material.system_id = %s
    '''
    return fetch_table(query, (system_id, ))

@systems_bp.route('/<int:system_id>/materials', methods = ['POST'])
def insert_material_in_system(system_id):
    body = request.get_json()
    name = body.get('name')
    note = body.get('note')
    
    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM systems WHERE id = %s)', (system_id,))
        system_exists = cursor.fetchone()[0]
        if not system_exists:
            return jsonify({"message": "System Not Found."}), 404
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM materials WHERE name = %s AND system_id = %s)', (name, system_id))
        material_exists = cursor.fetchone()[0]
        if material_exists:
            return jsonify({"message": "User with this name already exists."}), 401
        
        cursor.execute(
            'INSERT INTO materials (system_id, name, note) VALUES (%s, %s, %s)',
            (system_id, name, note)
        )
        connection.commit()
        return jsonify({"message": "seikou"}), 201
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
