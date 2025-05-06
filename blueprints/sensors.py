from flask import Blueprint, request, jsonify
from database import connect
from datetime import datetime

sensors_bp = Blueprint('sensors', __name__)

@sensors_bp.route('/<int:sensor_id>', methods=['PUT'])
def update_sensor(sensor_id):
    body = request.get_json()
    name = body.get('name')
    unit = body.get('unit')
    tank_id = body.get('tank_id')
    position = body.get('position')
    date = datetime.fromisoformat(body.get('date'))
    
    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute(
            "UPDATE sensors SET name = %s, unit = %s, tank_id = %s, position = %s, date = %s WHERE id = %s",
            (name, unit, tank_id, position, date, sensor_id)
        )

        connection.commit()
        return jsonify({"message": "Sensor updated successfully"}), 200
    except Exception as error:
        if connection:
            connection.rollback()
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



@sensors_bp.route('/<int:sensor_id>', methods = ['DELETE'])
def delete_sensor(sensor_id):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # 指定されたmaterial_idに対応するアイテムが存在するかチェック
        cursor.execute('SELECT EXISTS(SELECT 1 FROM sensors WHERE id = %s)', (sensor_id, ))
        sensor_exists = cursor.fetchone()[0]
        if not sensor_exists:
            return jsonify({"message": "Sensor Not Found"}), 404
        
        # アイテムを削除
        cursor.execute('DELETE FROM sensors WHERE id = %s', (sensor_id,))
        connection.commit()

        return jsonify({"message": "Sensor deleted successfully"}), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
