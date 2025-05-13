from flask import Blueprint, request, jsonify
from database import connect

operations_bp = Blueprint('operations', __name__)

def fetch_table(query, params = ()):
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    cursor.execute(query, params)
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

@operations_bp.route('', methods = ['GET'])
def fetch_operations():
    query = 'SELECT id, name, target_type FROM operations'
    return fetch_table(query, ())
