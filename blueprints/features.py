from flask import Blueprint, request, jsonify
from database import connect

features_bp = Blueprint('features', __name__)

def fetch_table(query, params = ()):
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    cursor.execute(query, params)
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result



@features_bp.route('', methods = ['GET'])
def fetch_features():
    query = 'SELECT id, name, unit FROM features'
    return fetch_table(query, ())
