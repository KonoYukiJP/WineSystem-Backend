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
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    
    query = 'SELECT id, name, target_type FROM operations'
    cursor.execute(query)
    operations = cursor.fetchall()
    
    for operation in operations:
        query = '''
            SELECT feature_id
            FROM operation_features
            WHERE operation_id = %s
        '''
        cursor.execute(query, (operation['id'], ))
        feature_ids = cursor.fetchall()
        
        operation['feature_ids'] = []
        for feature_id in feature_ids:
            operation['feature_ids'].append(feature_id['feature_id'])
        
    print(operations)
    
    cursor.close()
    connection.close()
    
    return operations
