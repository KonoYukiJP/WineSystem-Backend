from flask import Blueprint, request, jsonify
from database import connect

operations_bp = Blueprint('operations', __name__)

@operations_bp.route('', methods = ['GET'])
def fetch_operations():
    with (
        connect() as connection,
        connection.cursor(dictionary = True) as cursor
    ):
        query = 'SELECT id, name, target_type FROM operations'
        cursor.execute(query)
        operations = cursor.fetchall()
        
        for operation in operations:
            query = '''
                SELECT feature_id
                FROM operation_features
                WHERE operation_id = %s
            '''
            params = (operation['id'], )
            cursor.execute(query, params)
            feature_ids = cursor.fetchall()
            
            operation['feature_ids'] = []
            for feature_id in feature_ids:
                operation['feature_ids'].append(feature_id['feature_id'])
    
    return operations
