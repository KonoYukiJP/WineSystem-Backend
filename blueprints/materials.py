from flask import Blueprint, request, jsonify

from auth import authorization_required
from database import connect

materials_bp = Blueprint('materials', __name__)

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
