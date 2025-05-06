from flask import Blueprint, request, jsonify
from database import connect

actions_bp = Blueprint('actions', __name__)

def fetch_table(query, params = ()):
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    cursor.execute(query, params)
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

@actions_bp.route('', methods = ['GET'])
def fetch_actions():
    query = '''
        SELECT id, name
        FROM actions
    '''
    return fetch_table(query, ())
