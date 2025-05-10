from flask import Blueprint, request, jsonify
from database import connect

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/<int:role_id>', methods=['PATCH'])
def update_role(role_id):
    try:
        body = request.get_json()
        role_name = body.get('name')
        inserts = body.get('inserts')
        deletes = body.get('deletes')
        
        print(body)
        
        connection = connect()
        cursor = connection.cursor()
        connection.start_transaction()
        
        cursor.execute('UPDATE roles SET name = %s WHERE id = %s', (role_name, role_id))
        
        for permission in deletes:
            resource_id = permission['resource_id']
            action_ids = permission['action_ids']
            
            for action_id in action_ids:
                cursor.execute(
                    '''
                    DELETE FROM permissions
                    WHERE role_id = %s AND resource_id = %s AND action_id = %s
                    ''',
                    (role_id, action_id, resource_id)
                )
                
        for permission in inserts:
            resource_id = permission['resource_id']
            action_ids = permission['action_ids']
            
            for action_id in action_ids:
                cursor.execute(
                    '''
                    INSERT INTO permissions (role_id, resource_id, action_id)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE role_id = role_id
                    ''',
                    (role_id, resource_id, action_id)
                )
        
        connection.commit()
        
        return jsonify({"message": "Role updated successfully"}), 200

    except Exception as error:
        print(str(error))
        return jsonify({"message": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@roles_bp.route('/<int:role_id>', methods = ['DELETE'])
def delete_role(role_id):
    try:
        connection = connect()
        cursor = connection.cursor()
        
        # 指定されたmaterial_idに対応するアイテムが存在するかチェック
        cursor.execute('SELECT EXISTS(SELECT 1 FROM roles WHERE id = %s)', (role_id, ))
        sensor_exists = cursor.fetchone()[0]
        if not sensor_exists:
            return jsonify({"message": "Role Not Found"}), 404
        
        # アイテムを削除
        cursor.execute('DELETE FROM roles WHERE id = %s', (role_id, ))
        connection.commit()

        return jsonify({"message": "Role deleted successfully"}), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
