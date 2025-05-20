from flask import Blueprint, request, jsonify

from auth import authorization_required
from database import connect

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/<int:role_id>', methods = ['PATCH'])
@authorization_required('Role')
def update_role(role_id):
    body = request.get_json()
    role_name = body.get('name')
    inserts = body.get('inserts')
    deletes = body.get('deletes')
    
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            cursor.execute('UPDATE roles SET name = %s WHERE id = %s', (role_name, role_id))
            
            for permission in deletes:
                resource_id = permission['resource_id']
                action_ids = permission['action_ids']
                
                for action_id in action_ids:
                    query = '''
                        DELETE FROM permissions
                        WHERE role_id = %s AND resource_id = %s AND action_id = %s
                    '''
                    params = (role_id, resource_id, action_id)
                    cursor.execute(query, params)
                    
            for permission in inserts:
                resource_id = permission['resource_id']
                action_ids = permission['action_ids']
                
                for action_id in action_ids:
                    query = '''
                        INSERT INTO permissions (role_id, resource_id, action_id)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE role_id = role_id
                    '''
                    params = (role_id, resource_id, action_id)
                    cursor.execute(query, params)
    
            connection.commit()
        
        return jsonify({'message': 'Success'}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@roles_bp.route('/<int:role_id>', methods = ['DELETE'])
@authorization_required('Role')
def delete_role(role_id):
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'SELECT EXISTS (SELECT 1 FROM roles WHERE id = %s)'
            params = (role_id, )
            cursor.execute(query, params)
            sensor_exists = cursor.fetchone()[0]
            if not sensor_exists:
                return jsonify({"message": "Role Not Found"}), 404
            
            cursor.execute('DELETE FROM roles WHERE id = %s', (role_id, ))
            connection.commit()

        return jsonify({"message": "Role deleted successfully"}), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500
