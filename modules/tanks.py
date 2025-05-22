# tanks.py

from flask import Blueprint, request, jsonify

from database import connect, fetchall
from auth import authorization_required

tanks_bp = Blueprint('tanks', __name__)

@tanks_bp.route('', methods = ['GET'])
@authorization_required('Tank')
def get_tanks_in_system():
    system_id = request.user['system_id']
    query = '''
        SELECT id, name, note, material_id
        FROM tanks
        WHERE system_id = %s
    '''
    params = (system_id, )
    try:
        tanks = fetchall(query, params)
        return jsonify(tanks), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@tanks_bp.route('', methods = ['POST'])
@authorization_required('Tank')
def create_tank_in_system():
    system_id = request.user['system_id']
    body = request.get_json()
    
    try:
        name = body['name']
        note = body['note']
        material_id = body.get('material_id')
    except KeyError:
        return jsonify({'message': 'Invalid request format'}), 400

    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'SELECT EXISTS (SELECT 1 FROM systems WHERE id = %s)'
            params = (system_id, )
            cursor.execute(query, params)
            system_exists = cursor.fetchone()[0]
            if not system_exists:
                return jsonify({"message": "System Not Found."}), 404
            
            query = '''
                SELECT EXISTS (
                    SELECT 1 FROM tanks
                    WHERE name = %s AND system_id = %s
                )
            '''
            params = (name, system_id)
            cursor.execute(query, params)
            tank_exists = cursor.fetchone()[0]
            if tank_exists:
                return jsonify({"message": "This name is already taken."}), 409
            
            material_id = None if material_id == 0 else material_id
            
            query = '''
                INSERT INTO tanks (system_id, name, note, material_id)
                VALUES (%s, %s, %s, %s)
            '''
            params = (system_id, name, note, material_id)
            cursor.execute(query, params)
            connection.commit()
            
        return jsonify({'message': 'Success'}), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500

@tanks_bp.route('/<int:tank_id>', methods=['PUT'])
@authorization_required('Tank')
def update_tank(tank_id):
    body = request.get_json()
    
    try:
        tank_name = body['name']
        tank_note = body['note']
        material_id = body.get('material_id')
    except KeyError:
        return jsonify({'message': 'Invalid request format'}), 400

    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'UPDATE tanks SET name = %s, note = %s, material_id = %s WHERE id = %s'
            params = (tank_name, tank_note, material_id, tank_id)
            cursor.execute(query, params)
            connection.commit()
            
        return jsonify({"message": "Material updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@tanks_bp.route('/<int:tank_id>', methods = ['DELETE'])
@authorization_required('Tank')
def delete_tank(tank_id):
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'SELECT id FROM tanks WHERE id = %s'
            params = (tank_id, )
            cursor.execute(query, params)
            tank_exists = cursor.fetchone()
            if not tank_exists:
                return jsonify({"message": "Tank Not Found"}), 404
            
            cursor.execute('DELETE FROM tanks WHERE id = %s', (tank_id,))
            connection.commit()

        return jsonify({"message": "Tank deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
