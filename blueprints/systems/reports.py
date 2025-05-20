# reports.py

from datetime import datetime

from flask import Blueprint,request,jsonify

from . import systems_bp
from auth import authorization_required
from database import connect, fetchall
    
@systems_bp.route('/<int:system_id>/reports', methods = ['GET'])
@authorization_required('Report')
def get_reports_in_system(system_id):
    query = '''
        SELECT
            id,
            date, 
            user_id,
            work_id,
            operation_id,
            kind_id,
            feature_id,
            value,
            note
        FROM reports
        WHERE system_id = %s
    '''
    params = (system_id, )
    try:
        reports = fetchall(query, params)
        for report in reports:
            report['date'] = report['date'].strftime('%Y-%m-%dT%H:%M:%SZ')
        return jsonify(reports)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@systems_bp.route('/<int:system_id>/reports', methods = ['POST'])
@authorization_required('Report')
def create_report_in_system(system_id):
    body = request.get_json()
    try:
        date = datetime.fromisoformat(body['date'].replace("Z", "+00:00"))
        user_id = request.user['user_id']
        work_id = body['work_id']
        operation_id = body['operation_id']
        kind_id = body['kind_id']
        feature_id = body.get('feature_id')
        value = body.get('value')
        note = body['note']
    except (KeyError, ValueError, TypeError) as error:
        return jsonify({"message": str(error)}), 400
    
    try:
        with (
            connect() as connection,
            connection.cursor() as cursor
        ):
            query = '''
                INSERT INTO reports (
                    system_id,
                    date, 
                    user_id, 
                    work_id, 
                    operation_id, 
                    kind_id, 
                    feature_id, 
                    value, 
                    note
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            params = (system_id, date, user_id, work_id, operation_id, kind_id, feature_id, value, note)
            cursor.execute(query, params)
            connection.commit()
            
        return jsonify({"message": "Report was inserted successly"}), 201
    except Exception as error:
        return jsonify({"message": str(error)}), 500
