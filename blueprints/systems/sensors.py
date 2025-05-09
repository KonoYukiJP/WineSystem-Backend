from flask import Blueprint,request,jsonify
from database import connect
from datetime import datetime

from . import systems_bp

def fetch_table(query, params = ()):
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    cursor.execute(query, params)
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

@systems_bp.route('/<int:system_id>/sensors', methods = ['GET'])
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
    sensors = fetch_table(query, (system_id, ))
    for sensor in sensors:
        sensor['date'] = sensor['date'].strftime('%Y-%m-%dT%H:%M:%SZ')
    return jsonify(sensors)

@systems_bp.route('/<int:system_id>/sensors', methods = ['POST'])
def create_sensor_in_system(system_id):
    body = request.get_json()
    name = body.get('name')
    unit = body.get('unit')
    tank_id = body.get('tank_id', None)
    position = body.get('position')
    date = datetime.fromisoformat(body.get('date').replace("Z", "+00:00"))
    
    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM systems WHERE id = %s)', (system_id,))
        system_exists = cursor.fetchone()[0]
        if not system_exists:
            return jsonify({"message": "System Not Found."}), 404
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM sensors WHERE name = %s AND system_id = %s)', (name, system_id))
        sensor_exists = cursor.fetchone()[0]
        if sensor_exists:
            return jsonify({"message": "Sensor with this name already exists."}), 401
        
        cursor.execute(
            '''INSERT INTO sensors (system_id, name, unit, tank_id, position, date)
            VALUES (%s, %s, %s, %s, %s, %s)''',
            (system_id, name, unit, tank_id, position, date)
        )
        connection.commit()
        return jsonify({"message": "sensor was inserted successly"}), 201
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
