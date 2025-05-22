# actions.py

from flask import Blueprint, request, jsonify
from database import fetchall

actions_bp = Blueprint('actions', __name__)

@actions_bp.route('', methods = ['GET'])
def get_actions():
    try:
        query = '''
            SELECT id, name
            FROM actions
        '''
        actions = fetchall(query)
        return jsonify(actions), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
