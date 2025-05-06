from flask import Blueprint, request, jsonify
from database import connect

works_bp = Blueprint('works', __name__)

def fetch_table(query, params = ()):
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    cursor.execute(query, params)
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

@works_bp.route('', methods = ['GET'])
def fetch_works():
    query = 'SELECT id, name FROM works'
    return fetch_table(query, ())

@works_bp.route('/<int:work_id>/operations', methods = ['GET'])
def fetch_operations_in_work(work_id):
    query = 'SELECT id, work_id, name FROM operations WHERE work_id = %s'
    return fetch_table(query, (work_id, ))
