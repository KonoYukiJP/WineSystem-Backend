from flask import Blueprint, request, jsonify
from database import connect

materials_bp = Blueprint('materials', __name__)

@materials_bp.route('/<int:material_id>', methods=['PUT'])
def update_material(material_id):
    body = request.get_json()
    material_name = body.get('name')
    material_note = body.get('note')

    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute(
            'UPDATE materials SET name = %s, note = %s WHERE id = %s',
            (material_name, material_note, material_id)
        )

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

@materials_bp.route('/<int:material_id>', methods = ['DELETE'])
def delete_material(material_id):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # 指定されたmaterial_idに対応するアイテムが存在するかチェック
        cursor.execute('SELECT id FROM materials WHERE id = %s', (material_id,))
        material = cursor.fetchone()
        if not material:
            return jsonify({"status": "Error", "message": "Material not found"}), 404
        
        # アイテムを削除
        cursor.execute('DELETE FROM materials WHERE id = %s', (material_id,))
        connection.commit()

        return jsonify({"status": "Success", "message": "Material deleted successfully"}), 200
    except Exception as error:
        return jsonify({"status": "Error", "message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
