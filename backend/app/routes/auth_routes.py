from flask import Blueprint, request, jsonify
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    result, status = AuthController.login(data['email'], data['password'])
    return jsonify(result), status

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Email, name, and password required'}), 400
    
    result, status = AuthController.register(
        data['email'],
        data['name'],
        data['password'],
        data.get('role', 'user')
    )
    return jsonify(result), status
