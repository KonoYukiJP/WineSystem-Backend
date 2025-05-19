# reports.py

from datetime import datetime

from flask import Blueprint, request, jsonify

from auth import authorization_required
from database import connect

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/<int:report_id>', methods=['PUT'])
@authorization_required('Report')
def update_report(report_id):
    body = request.get_json()
    
    try:
        date = datetime.fromisoformat(body['date'].replace("Z", "+00:00"))
        user_id = body['user_id']
        work_id = body['work_id']
        operation_id = body['operation_id']
        kind_id = body['kind_id']
        feature_id = body['feature_id']
        value = body['value']
        note = body['note']
    except (KeyError, ValueError, TypeError) as error:
        return jsonify({"message": str(error)}), 400
    
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
    params = (date, user_id, work_id, operation_id, kind_id, feature_id, value, note, report_id)
    
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            cursor.execute(query, params)
            connection.commit()
            
        return jsonify({"message": "Report updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@materials_bp.route('/<int:report_id>', methods = ['DELETE'])
@authorization_required('Report')
def delete_report(report_id):
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = 'SELECT EXISTS (SELECT 1 FROM reports WHERE id = %s)'
            params = (report_id, )
            cursor.execute(query, params)
            report_exists = cursor.fetchone()
            
            if not report_exists:
                return jsonify({"message": "Report Not Found"}), 404
            
            query = 'DELETE FROM reports WHERE id = %s'
            params = (report_id, )
            cursor.execute(query, params)
            connection.commit()

        return jsonify({"message": "Report deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
