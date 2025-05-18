from flask import Blueprint, request, jsonify
from database import connect, fetchall

works_bp = Blueprint('works', __name__)

@works_bp.route('', methods = ['GET'])
def fetch_works():
    try:
        with (
            connect() as connection,
            connection.cursor(dictionary = True) as cursor
        ):
            query = 'SELECT id, name FROM works'
            cursor.execute(query)
            works = cursor.fetchall()
            
            for work in works:
                query = '''
                    SELECT operation_id
                    FROM work_operations
                    WHERE work_id = %s
                '''
                params = (work['id'], )
                cursor.execute(query, params)
                operation_ids = cursor.fetchall()
                
                work['operation_ids'] = []
                for operation_id in operation_ids:
                    work['operation_ids'].append(operation_id['operation_id'])
    
        return works
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@works_bp.route('/<int:work_id>/operations', methods = ['GET'])
def fetch_operations_in_work(work_id):
    query = 'SELECT id, work_id, name FROM operations WHERE work_id = %s'
    return fetchall(query, (work_id, ))
