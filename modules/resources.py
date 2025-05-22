# resource.py

from flask import Blueprint, request, jsonify
from database import fetchall

resources_bp = Blueprint('resources', __name__)

@resources_bp.route('', methods = ['GET'])
def get_resources():
    query = '''
        SELECT id, name
        FROM resources resource
    '''
    try:
        resources = fetchall(query)
        return jsonify(resources), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
