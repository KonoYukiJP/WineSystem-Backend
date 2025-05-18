# sensors.py

from datetime import datetime

from flask import Blueprint,request,jsonify

from . import systems_bp
from auth import authorization_required
from database import connect, fetchall

@systems_bp.route('/<int:system_id>/sensors', methods = ['GET'])
@authorization_required('Sensor')
def get_sensors_in_system(system_id):
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
        return jsonify(sensors), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@systems_bp.route('/<int:system_id>/sensors', methods = ['POST'])
@authorization_required('Sensor')
def create_sensor_in_system(system_id):
    body = request.get_json()
    
    try:
        name = body['name']
        unit = body['unit']
        tank_id = body['tank_id']
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
