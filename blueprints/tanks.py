from flask import Blueprint, request, jsonify

from database import connect
from auth import authorization_required

tanks_bp = Blueprint('tanks', __name__)

@tanks_bp.route('/<int:tank_id>', methods=['PUT'])
@authorization_required('Tank')
def update_tank(tank_id):
    body = request.get_json()
    
    try:
        tank_name = body.get('name')
        tank_note = body.get('note')
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
