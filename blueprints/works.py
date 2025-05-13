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
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    
    query = 'SELECT id, name FROM works'
    cursor.execute(query)
    works = cursor.fetchall()
    
    for work in works:
        query = '''
            SELECT operation_id
            FROM work_operations
            WHERE work_id = %s
        '''
        cursor.execute(query, (work['id'], ))
        operation_ids = cursor.fetchall()
        work['operation_ids'] = []
        for operation_id in operation_ids:
            work['operation_ids'].append(operation_id['operation_id'])
        
    print(works)
    
    cursor.close()
    connection.close()
    
    return works

@works_bp.route('/<int:work_id>/operations', methods = ['GET'])
def fetch_operations_in_work(work_id):
    query = 'SELECT id, work_id, name FROM operations WHERE work_id = %s'
    return fetch_table(query, (work_id, ))
