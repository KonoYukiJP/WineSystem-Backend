from flask import Blueprint, request, jsonify
from database import connect

resources_bp = Blueprint('resources', __name__)

def fetch_table(query, params = ()):
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    cursor.execute(query, params)
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

@resources_bp.route('', methods = ['GET'])
def fetch_resources():
    query = '''
        SELECT id, name
        FROM resources resource
    '''
    return fetch_table(query, ())
