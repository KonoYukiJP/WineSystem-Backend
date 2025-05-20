from flask import Blueprint, request, jsonify
from database import connect, fetchall
import subprocess
import datetime
import os

from auth import authorization_required

backups_bp = Blueprint('backups', __name__)

@backups_bp.route('', methods = ['POST'])
@authorization_required('Backup')
def create_backup():
    try:
        query = 'SELECT name FROM users AS user WHERE user.id = %s'
        params = (request.user['id'], )
        user = fetchall(query, params)[0]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        backup_file = os.path.join('backups', f"backup_at_{timestamp}_by_{user['name']}.sql")

        cmd = [
            'mysqldump',
            '--no-tablespaces',
            '-u', 'flask_user',
            '-pP@ssw0rd',
            'wine_database'
        ]

        with open(backup_file, "w") as f:
            subprocess.run(cmd, stdout=f, check=True)

        return backup_file
    except Exception as e:
        print(str(e))
        return jsonify({"message": str(e)}), 500

@backups_bp.route('', methods=['GET'])
@authorization_required('Backup')
def list_backups():
    backup_dir = "/var/www/WineSystem-Backend/backups"

    try:
        # backups フォルダ内の .sql ファイルを取得してソート
        files = sorted([
            f for f in os.listdir(backup_dir)
            if f.endswith(".sql")
        ], reverse=True)
        
        print({"backups": files})
        return jsonify({"backups": files}), 200

    except Exception as e:
        print(str(e))
        return jsonify({"message": str(e)}), 500

@backups_bp.route('', methods=['PUT'])
@authorization_required('Backup')
def restore_backup():
    data = request.get_json()
    filename = data.get('filename')

    backup_file = os.path.join("/var/www/WineSystem-Backend/backups", filename)

    if not os.path.exists(backup_file):
        print("404")
        return jsonify({"error": "ファイルが存在しません"}), 404

    try:
        cmd = [
            '/usr/bin/mysql',
            '-u', 'flask_user',
            '-pP@ssw0rd',
            'wine_database'
        ]
        with open(backup_file, "r") as f:
            subprocess.run(cmd, stdin=f, check=True)

        return jsonify({"message": "復元完了"}), 200

    except Exception as e:
        print(str(e))
        return jsonify({"message": str(e)}), 500

@backups_bp.route('/<string:filename>', methods=['DELETE'])
@authorization_required('Backup')
def delete_backup(filename):
    print(filename)

    if not filename:
        return jsonify({"error": "'filename' が必要です"}), 400

    backup_file = os.path.join("/var/www/WineSystem-Backend/backups", filename)

    if not os.path.exists(backup_file):
        return jsonify({"error": "ファイルが存在しません"}), 404

    try:
        os.remove(backup_file)
        return jsonify({"message": "削除しました"}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"message": str(e)}), 500
