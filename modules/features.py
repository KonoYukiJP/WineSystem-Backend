# features.py

from flask import Blueprint, request, jsonify
from database import fetchall

features_bp = Blueprint('features', __name__)

@features_bp.route('', methods = ['GET'])
def get_features():
    try:
        query = 'SELECT id, name, unit FROM features'
        features = fetchall(query)
        return jsonify(features), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
