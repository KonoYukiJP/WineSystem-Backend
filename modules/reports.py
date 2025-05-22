# reports.py

from datetime import datetime

from flask import Blueprint, request, jsonify

from auth import authorization_required
from database import connect, fetchall

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('', methods = ['GET'])
@authorization_required('Report')
def get_reports():
    system_id = request.user['system_id']
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

@reports_bp.route('', methods = ['POST'])
@authorization_required('Report')
def create_report():
    system_id = request.user['system_id']
    body = request.get_json()
    try:
        date = datetime.fromisoformat(body['date'].replace("Z", "+00:00"))
        user_id = request.user['id']
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
        feature_id = body.get('feature_id')
        value = body.get('value')
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

@reports_bp.route('/<int:report_id>', methods = ['DELETE'])
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
