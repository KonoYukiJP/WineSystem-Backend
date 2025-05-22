# materials.py

from flask import Blueprint, request, jsonify

from auth import authorization_required
from database import connect, fetchall

materials_bp = Blueprint('materials', __name__)

@materials_bp.route('', methods = ['GET'])
@authorization_required(resource = 'Material')
def get_materials():
    system_id = request.user['system_id']
    query = '''
        SELECT id, name, note
        FROM materials
        WHERE system_id = %s
    '''
    params = (system_id, )
    try:
        materials = fetchall(query, params)
        return jsonify(materials), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@materials_bp.route('', methods = ['POST'])
@authorization_required(resource = 'Material')
def create_material():
    system_id = request.user['system_id']
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

@materials_bp.route('/<int:material_id>', methods=['PUT'])
@authorization_required('Material')
def update_material(material_id):
    body = request.get_json()
    try:
        material_name = body['name']
        material_note = body['note']
    except KeyError:
        return jsonify({'message': 'Invalid request format'}), 400
        
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'UPDATE materials SET name = %s, note = %s WHERE id = %s'
            params = (material_name, material_note, material_id)
            cursor.execute(query, params)
            connection.commit()
            
        return jsonify({"message": "Material updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@materials_bp.route('/<int:material_id>', methods = ['DELETE'])
@authorization_required('Material')
def delete_material(material_id):
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'SELECT EXISTS (SELECT 1 FROM materials WHERE id = %s)'
            params = (material_id, )
            cursor.execute(query, params)
            material_exists = cursor.fetchone()
            
            if not material_exists:
                return jsonify({"message": "Material Not Found"}), 404
            
            query = 'DELETE FROM materials WHERE id = %s'
            params = (material_id, )
            cursor.execute(query, params)
            connection.commit()

        return jsonify({"message": "Material deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
