from flask import Blueprint, request, jsonify
from database import connect
import subprocess
import datetime
import os

backups_bp = Blueprint('backups', __name__)

@backups_bp.route('', methods = ['POST'])
def create_backup():
    backup_dir = "/var/www/WineSystem-Backend/backups"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")

    cmd = [
        'mysqldump',
        '-u', 'flask_user',
        '-pP@ssw0rd',
        'wine_database'
    ]

    with open(backup_file, "w") as f:
        subprocess.run(cmd, stdout=f, check=True)

    return backup_file
