# systems.backups.py

import datetime
import json
import os

from flask import Blueprint, request, jsonify

from . import systems_bp
from auth import authorization_required
from database import connect, fetchall

@systems_bp.route('/<int:system_id>/backups', methods = ['POST'])
@authorization_required('Backup')
def export_system_backup(system_id):
    user_id = request.user['id']
    body = request.get_json()
    try:
        username = body['username']
        note = body['note']
    except KeyError:
        return jsonify({'message': 'Invalid request format'}), 400

    try:
        datetime_now = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
        filename = f'{datetime_now}.json'
        
        result = {}
        result['info'] = {
            "filename": filename,
            "created_by": username,
            "created_at": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            "note": note
        }
        result['systems'] = fetchall('SELECT * FROM systems WHERE id = %s', (system_id, ))
        result['roles'] = fetchall('SELECT * FROM roles WHERE system_id = %s', (system_id, ))
        result['users'] = fetchall('SELECT * FROM users WHERE system_id = %s', (system_id, ))
        result['permissions'] = fetchall(
            '''
                SELECT permission.*
                FROM permissions permission
                JOIN roles role ON permission.role_id = role.id
                WHERE role.system_id = %s
            ''',
            (system_id, )
        )
        result['materials'] = fetchall('SELECT * FROM materials WHERE system_id = %s', (system_id, ))
        result['tanks'] = fetchall('SELECT * FROM tanks WHERE system_id = %s', (system_id, ))
        result['sensors'] = fetchall('SELECT * FROM sensors WHERE system_id = %s', (system_id, ))
        result['reports'] = fetchall('SELECT * FROM reports WHERE system_id = %s', (system_id, ))

        backup_dir = os.path.join('backups', f'system_{system_id}')
        os.makedirs(backup_dir, exist_ok = True)
        
        filepath = os.path.join(backup_dir, filename)
        
        with open(filepath, 'w', encoding = 'utf-8') as f:
            json.dump(result, f, ensure_ascii = False, indent = 2, default = str)
        
        return jsonify({"message": "バックアップ完了", "file": filename})

    except Exception as e:
        print(str(e))
        return jsonify({"message": str(e)}), 500

@systems_bp.route('/<int:system_id>/backups', methods = ['GET'])
@authorization_required('Backup')
def list_backups(system_id):
    backup_dir = os.path.join('backups', f'system_{system_id}')
    filenames = sorted([
        f for f in os.listdir(backup_dir)
        if f.endswith('.json')
    ], reverse = True)
    
    backups = []
    for filename in filenames:
        filepath = os.path.join(backup_dir, filename)

        info = {
            "filename": filename,
            "created_at": None,
            "created_by": None,
            "note": ""
        }

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding = 'utf-8') as f:
                try:
                    data = json.load(f)
                    info = data.get('info', {})
                except Exception:
                    pass

        backups.append(info)
    print(backups)
    return jsonify(backups), 200

@systems_bp.route('/<int:system_id>/backups/<string:filename>', methods = ['DELETE'])
@authorization_required('Backup')
def delete_backup(system_id, filename):
    backup_dir = os.path.join('backups', f'system_{system_id}')
    filepath = os.path.join(backup_dir, filename)

    if not os.path.exists(filepath):
        return jsonify({"message": "file doesn't exist."}), 404

    try:
        os.remove(filepath)
        return jsonify({"message": "削除しました"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# バックアップファイルから復元
@systems_bp.route('/<int:system_id>/backups/<string:filename>', methods = ['PUT'])
@authorization_required('Backup')
def restore_system_backup(system_id, filename):
    try:
        backup_dir = os.path.join('backups', f'system_{system_id}')
        filepath = os.path.join(backup_dir, filename)

        if not os.path.exists(filepath):
            return jsonify({"message": "file doesn't exist"}), 404

        with open(filepath, "r", encoding = "utf-8") as f:
            backup_data = json.load(f)
            
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            cursor.execute(
                '''
                    DELETE permission FROM permissions permission
                    JOIN roles role ON permission.role_id = role.id
                    WHERE role.system_id = %s
                ''',
                (system_id, )
            )
            cursor.execute('DELETE FROM users WHERE system_id = %s', (system_id, ))
            cursor.execute('DELETE FROM systems WHERE id = %s', (system_id,))
            
            ordered_tables = ["systems", "roles", "users", "permissions", "materials", "tanks", "sensors", "reports"]
            for table in ordered_tables:
                rows = backup_data.get(table)
                if not rows:
                    continue
                columns = rows[0].keys()
                placeholders = ", ".join(["%s"] * len(columns))
                column_list = ", ".join(columns)
                insert_sql = f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})"
                values = [tuple(row[col] for col in columns) for row in rows]
                cursor.executemany(insert_sql, values)

            connection.commit()

        return jsonify({"message": f"{filename} を復元しました"}), 200

    except Exception as e:
        print(f"復元エラー: {e}")
        return jsonify({"error": str(e)}), 500
