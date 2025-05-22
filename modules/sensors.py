# sensors.py

from datetime import datetime

from flask import Blueprint, request, jsonify

from database import connect, fetchall
from auth import authorization_required

sensors_bp = Blueprint('sensors', __name__)

@sensors_bp.route('', methods = ['GET'])
@authorization_required('Sensor')
def get_sensors():
    system_id  = request.user['system_id']
    query = '''
        SELECT
            id, 
            name, 
            unit, 
            tank_id, 
            position, 
            date
        FROM sensors
        WHERE system_id = %s
    '''
    params = (system_id, )
    try:
        sensors = fetchall(query, params)
        for sensor in sensors:
            sensor['date'] = sensor['date'].strftime('%Y-%m-%dT%H:%M:%SZ')
        print(sensors)
        return jsonify(sensors), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@sensors_bp.route('', methods = ['POST'])
@authorization_required('Sensor')
def create_sensor():
    system_id = request.user['system_id']
    body = request.get_json()
    
    try:
        name = body['name']
        unit = body['unit']
        tank_id = body.get('tank_id')
        position = body['position']
        date = datetime.fromisoformat(body['date'].replace("Z", "+00:00"))
    except (KeyError, ValueError, TypeError) as error:
        return jsonify({"message": str(error)}), 400
    
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
        
            query = 'SELECT EXISTS (SELECT 1 FROM sensors WHERE name = %s AND system_id = %s)'
            params = (name, system_id)
            cursor.execute(query, params)
            sensor_exists = cursor.fetchone()[0]
            if sensor_exists:
                return jsonify({"message": "This name is already taken."}), 401
            
            query = '''
                INSERT INTO sensors (system_id, name, unit, tank_id, position, date)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
            params = (system_id, name, unit, tank_id, position, date)
            cursor.execute(query, params)
            connection.commit()
            
        return jsonify({'message': 'Success'}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@sensors_bp.route('/<int:sensor_id>', methods=['PUT'])
@authorization_required('Sensor')
def update_sensor(sensor_id):
    body = request.get_json()
    
    try:
        name = body['name']
        unit = body['unit']
        tank_id = body.get('tank_id')
        position = body['position']
        date = datetime.fromisoformat(body['date'].replace('Z', '+00:00'))
    except (KeyError, ValueError, TypeError) as error:
        return jsonify({"message": str(error)}), 400
    
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'UPDATE sensors SET name = %s, unit = %s, tank_id = %s, position = %s, date = %s WHERE id = %s'
            params = (name, unit, tank_id, position, date, sensor_id)
            cursor.execute(query, params)
            connection.commit()
            
        return jsonify({'message': 'Sensor updated successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@sensors_bp.route('/<int:sensor_id>', methods = ['DELETE'])
@authorization_required('Sensor')
def delete_sensor(sensor_id):
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'SELECT EXISTS(SELECT 1 FROM sensors WHERE id = %s)'
            params = (sensor_id, )
            cursor.execute(query, params)
            sensor_exists = cursor.fetchone()[0]
            if not sensor_exists:
                return jsonify({"message": "Sensor Not Found"}), 404
            
            cursor.execute('DELETE FROM sensors WHERE id = %s', (sensor_id,))
            connection.commit()

        return jsonify({"message": "Sensor deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
