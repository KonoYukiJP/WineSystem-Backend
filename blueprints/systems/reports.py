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
            report.id, report.date, 
            user.id AS user_id,
            user.name AS username,
            work.id AS work_id,
            work.name AS work_name,
            operation.id AS operation_id,
            operation.name AS operation_name,
            report.kind_id AS kind_id,
            feature.id AS feature_id,
            feature.name AS feature_name,
            report.value,
            feature.unit,
            report.note
        FROM reports report
        JOIN users user ON report.user_id = user.id
        JOIN works work ON report.work_id = work.id
        JOIN operations operation ON report.operation_id = operation.id
        LEFT JOIN features feature ON report.feature_id = feature.id
        WHERE report.system_id = %s
    '''
    reports = fetch_table(query, (system_id, ))
    for report in reports:
        report['date'] = report['date'].strftime('%Y-%m-%dT%H:%M:%SZ')
        if report['work_id'] == 1:
            query = 'SELECT name FROM materials WHERE id = %s'
            materials = fetch_table(query, (report['kind_id'], ))
            report['kind_name'] = materials[0]['name']
        else:
            query = 'SELECT name FROM tanks WHERE id = %s'
            tanks = fetch_table(query, (report['kind_id'], ))
            report['kind_name'] = tanks[0]['name']
    return jsonify(reports)

@systems_bp.route('/<int:system_id>/reports', methods = ['POST'])
def insert_report_in_system(system_id):
    body = request.get_json()
    date = datetime.fromisoformat(body.get('date'))
    user_id = body.get('user_id')
    work_id = body.get('work_id')
    operation_id = body.get('operation_id')
    kind_id = body.get('kind')
    feature_id = body.get('feature_id')
    value = body.get('value')
    note = body.get('note')
    
    print(body)
    print(date, user_id, work_id, operation_id, kind_id, feature_id, value, note)
    
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
