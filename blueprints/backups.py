from flask import Blueprint, request, jsonify
from database import connect
import subprocess
import datetime
import os

backups_bp = Blueprint('backups', __name__)

@backups_bp.route('', methods = ['POST'])
def create_backup():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join('backups', f"backup_{timestamp}.sql")

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

@backups_bp.route('', methods=['GET'])
def list_backups():
    backup_dir = "/var/www/WineSystem-Backend/backups"

    try:
        # backups フォルダ内の .sql ファイルを取得してソート
        files = sorted([
            f for f in os.listdir(backup_dir)
            if f.endswith(".sql")
        ], reverse=True)

        return jsonify({"backups": files}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
