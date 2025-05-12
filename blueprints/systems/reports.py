from flask import Blueprint,request,jsonify
from database import connect
from datetime import datetime

from . import systems_bp

def fetch_table(query, params = ()):
    connection = connect()
    cursor = connection.cursor(dictionary = True)
    cursor.execute(query, params)
    
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result
    
@systems_bp.route('/<int:system_id>/reports', methods = ['GET'])
def fetch_reports_in_system(system_id):
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
        WHERE report.system_id = %s
    '''
    reports = fetch_table(query, (system_id, ))
    for report in reports:
        report['date'] = report['date'].strftime('%Y-%m-%dT%H:%M:%SZ')
    return jsonify(reports)

@systems_bp.route('/<int:system_id>/reports', methods = ['POST'])
def insert_report_in_system(system_id):
    body = request.get_json()
    date = datetime.fromisoformat(body.get('date').replace("Z", "+00:00"))
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
        
        cursor.execute(
            '''INSERT INTO reports (system_id, date, user_id, work_id, operation_id, kind_id, feature_id, value, note)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (system_id, date, user_id, work_id, operation_id, kind_id, feature_id, value, note)
        )
        connection.commit()
        return jsonify({"message": "Report was inserted successly"}), 201
    except Exception as error:
        return jsonify({"message": str(error)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
