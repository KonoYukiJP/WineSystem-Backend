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



@systems_bp.route('/<system_id>/tanks', methods = ['GET'])
def fetch_tanks_in_system(system_id):
    query = '''
        SELECT tank.id, tank.name, tank.note, tank.material_id
        FROM tanks tank
        WHERE tank.system_id = %s
    '''
    return fetch_table(query, (system_id, ))

@systems_bp.route('/<int:system_id>/tanks', methods = ['POST'])
def insert_tank_in_system(system_id):
    body = request.get_json()
    name = body.get('name')
    note = body.get('note')
    material_id = body.get('material_id')

    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM systems WHERE id = %s)', (system_id,))
        system_exists = cursor.fetchone()[0]
        if not system_exists:
            return jsonify({"message": "System Not Found."}), 404
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM tanks WHERE name = %s AND system_id = %s)', (name, system_id))
        tank_exists = cursor.fetchone()[0]
        if tank_exists:
            return jsonify({"status": "error", "message": "Tank with this name already exists."}), 401
        
        material_id = None if material_id == 0 else material_id
        
        cursor.execute('INSERT INTO tanks (system_id, name, note, material_id) VALUES (%s, %s, %s, %s)', (system_id, name, note, material_id))
        connection.commit()
        return jsonify({"message": "cursor.lastrowid"}), 201
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
