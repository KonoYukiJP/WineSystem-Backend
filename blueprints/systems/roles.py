from flask import Blueprint,request,jsonify
from database import connect

from . import systems_bp

def fetch_table(query, params = ()):
    with (
        connect() as connection,
        connection.cursor(dictionary = True) as cursor
    ):
        cursor.execute(query, params)
        result = cursor.fetchall()
    return result
    
@systems_bp.route('/<int:system_id>/roles', methods = ['GET'])
def get_roles_in_system(system_id):
    try:
        query = '''
            SELECT role.id, role.name
            FROM roles role
            WHERE role.system_id = %s
        '''
        params = (system_id, )
        roles = fetch_table(query, params)
        
        with (
            connect() as connection,
            connection.cursor(dictionary = True) as cursor
        ):
            for role in roles:
                query = '''
                    SELECT permission.resource_id, permission.action_id
                    FROM permissions permission
                    WHERE permission.role_id = %s
                '''
                params = (role['id'], )
                cursor.execute(query, params)
                raw_permissions = cursor.fetchall()

                # resource_id ごとに group 化（dict[int, list[int]]）
                permission_map = {}
                for permission in raw_permissions:
                    resource_id = permission['resource_id']
                    action_id = permission['action_id']
                    if resource_id not in permission_map:
                        permission_map[resource_id] = []
                    permission_map[resource_id].append(action_id)

                # dict を list of dict に変換
                grouped_permissions = [
                    {
                        "resource_id": resource_id,
                        "action_ids": action_ids
                    }
                    for resource_id, action_ids in permission_map.items()
                ]

                # ロールに追加
                role['permissions'] = grouped_permissions
        
        return jsonify(roles), 200
    except Exception as error:
        return jsonify({"message": str(error)}), 500

@systems_bp.route('/<int:system_id>/roles', methods = ['POST'])
def insert_role_in_system(system_id):
    body = request.get_json()
    name = body.get('name')

    try:
        connection = connect()
        cursor = connection.cursor()
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM systems WHERE id = %s)', (system_id,))
        system_exists = cursor.fetchone()[0]
        if not system_exists:
            return jsonify({"message": "System Not Found."}), 404
        
        cursor.execute('SELECT EXISTS (SELECT 1 FROM roles WHERE name = %s AND system_id = %s)', (name, system_id))
        role_exists = cursor.fetchone()[0]
        if role_exists:
            return jsonify({"message": "Role with this name already exists."}), 401
        
        cursor.execute('INSERT INTO roles (system_id, name) VALUES (%s, %s)', (system_id, name))
        connection.commit()
        return jsonify({"message": "Role was inserted successly"}), 201
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


