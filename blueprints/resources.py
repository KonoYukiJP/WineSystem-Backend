from flask import Blueprint, request, jsonify
from database import connect, fetchall

resources_bp = Blueprint('resources', __name__)

@resources_bp.route('', methods = ['GET'])
def fetch_resources():
    query = '''
        SELECT id, name
        FROM resources resource
    '''
    return fetchall(query, ())
