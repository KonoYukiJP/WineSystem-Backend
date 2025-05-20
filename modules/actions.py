# actions.py

from flask import Blueprint, request, jsonify
from database import connect, fetchall

actions_bp = Blueprint('actions', __name__)

@actions_bp.route('', methods = ['GET'])
def fetch_actions():
    query = '''
        SELECT id, name
        FROM actions
    '''
    return fetchall(query, ())
