from flask import Blueprint, request, jsonify
from database import connect
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    body = request.get_json()
    date = datetime.fromisoformat(body.get('date'))
    user_id = body.get('user_id')
    work_id = body.get('work_id')
    operation_id = body.get('operation_id')
    kind_id = body.get('kind_id')
    feature_id = body.get('feature_id')
    value = body.get('value')
    note = body.get('note')
    
    try:
        connection = connect()
        cursor = connection.cursor()
        query = '''
            UPDATE reports
            SET 
                date = %s, 
                user_id = %s,
                work_id = %s,
                operation_id = %s,
                kind_id = %s,
                feature_id = %s,
                value = %s,
                note = %s
            WHERE id = %s
        '''
        cursor.execute(query, (date, user_id, work_id, operation_id, kind_id, feature_id, value, note, report_id))

        connection.commit()
        return jsonify({"message": "Report updated successfully"}), 200

    except Exception as error:
        if connection:
            connection.rollback()
        print(str(error))
        return jsonify({"message": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
