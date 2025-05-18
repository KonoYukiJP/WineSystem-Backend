# features.py

from flask import Blueprint, request, jsonify
from database import connect, fetchall

features_bp = Blueprint('features', __name__)

@features_bp.route('', methods = ['GET'])
def fetch_features():
    query = 'SELECT id, name, unit FROM features'
    return fetchall(query, ())
