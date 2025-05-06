from flask import Blueprint, request, jsonify
from database import connect

tanks_bp = Blueprint('tanks', __name__)

@tanks_bp.route('/<int:tank_id>', methods=['PUT'])
def update_tank(tank_id):
    body = request.get_json()
    tank_name = body.get('name')
    tank_note = body.get('note')
    material_id = body.get('material_id')

    try:
        connection = connect()
        cursor = connection.cursor()

        cursor.execute('UPDATE tanks SET name = %s, note = %s, material_id = %s WHERE id = %s', (tank_name, tank_note, material_id, tank_id))

        connection.commit()
        return jsonify({"message": "Material updated successfully"}), 200

    except Exception as error:
        if connection:
            connection.rollback()
        return jsonify({"message": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@tanks_bp.route('/<int:tank_id>', methods = ['DELETE'])
def delete_tank(tank_id):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # 指定されたmaterial_idに対応するアイテムが存在するかチェック
        cursor.execute('SELECT id FROM tanks WHERE id = %s', (tank_id,))
        tank = cursor.fetchone()
        if not tank:
            return jsonify({"status": "Error", "message": "Tank not found"}), 404
        
        # アイテムを削除
        cursor.execute('DELETE FROM tanks WHERE id = %s', (tank_id,))
        connection.commit()

        return jsonify({"status": "Success", "message": "Tank deleted successfully"}), 200
    except Exception as error:
        return jsonify({"status": "Error", "message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
