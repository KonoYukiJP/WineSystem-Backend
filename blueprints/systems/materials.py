# materials.py

from flask import Blueprint, request, jsonify

from . import systems_bp
from auth import authorization_required
from database import connect

@systems_bp.route('/<int:system_id>/materials', methods = ['GET'])
@authorization_required(resource = 'Material')
def get_materials_in_system(system_id):
    query = '''
        SELECT id, name, note
        FROM materials
        WHERE system_id = %s
    '''
    params = (system_id, )
    try:
        with (
            connect() as connection,
            connection.cursor(dictionary = True) as cursor
        ):
            cursor.execute(query, params)
            materials = cursor.fetchall()
        return jsonify(materials), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@systems_bp.route('/<int:system_id>/materials', methods = ['POST'])
@authorization_required(resource = 'Material')
def create_material_in_system(system_id):
    body = request.get_json()
    
    try:
        name = body['name']
        note = body['note']
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
                    SELECT 1 FROM materials
                    WHERE name = %s AND system_id = %s
                )
            '''
            params = (name, system_id)
            cursor.execute(query, params)
            material_exists = cursor.fetchone()[0]
            if material_exists:
                return jsonify({"message": "This name is already taken."}), 409
            
            query = '''
                INSERT INTO materials (system_id, name, note)
                VALUES (%s, %s, %s)
            '''
            params = (system_id, name, note)
            cursor.execute(query, params)
            connection.commit()
            
        return jsonify({'message': 'Success'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500
