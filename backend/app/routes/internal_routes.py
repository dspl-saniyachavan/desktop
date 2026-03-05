from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.parameter import Parameter
from app.models import db

internal_bp = Blueprint('internal', __name__, url_prefix='/api/internal')

@internal_bp.route('/parameters', methods=['GET'])
def get_parameters():
    """Internal endpoint to get parameters without authentication"""
    try:
        parameters = Parameter.query.all()
        return jsonify({
            'parameters': [
                {
                    'id': p.id,
                    'name': p.name,
                    'unit': p.unit,
                    'description': p.description,
                    'enabled': p.enabled
                }
                for p in parameters
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch parameters: {str(e)}'}), 500

@internal_bp.route('/sync-user', methods=['POST'])
def sync_user():
    """Internal endpoint to sync user from desktop"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('name'):
        return jsonify({'error': 'Email and name required'}), 400
    
    try:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'message': 'User already exists'}), 200
        
        user = User(
            email=data['email'],
            name=data['name'],
            password_hash=data.get('password_hash', ''),
            role=data.get('role', 'user')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User synced successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500

@internal_bp.route('/sync-user-role', methods=['PUT'])
def sync_user_role():
    """Internal endpoint to sync user role update"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('role'):
        return jsonify({'error': 'Email and role required'}), 400
    
    try:
        user = User.query.filter_by(email=data['email']).first()
        if user:
            user.role = data['role']
            db.session.commit()
            return jsonify({'message': 'User role synced successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500

@internal_bp.route('/sync-user-delete', methods=['DELETE'])
def sync_user_delete():
    """Internal endpoint to sync user deletion"""
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email required'}), 400
    
    try:
        user = User.query.filter_by(email=data['email']).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

@internal_bp.route('/sync-parameter', methods=['POST'])
def sync_parameter_create():
    """Internal endpoint to create new parameter from desktop"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('unit'):
        return jsonify({'error': 'Parameter name and unit required'}), 400
    
    try:
        existing_param = Parameter.query.filter_by(name=data['name']).first()
        if existing_param:
            return jsonify({'message': 'Parameter already exists'}), 200
        
        param = Parameter(
            name=data['name'],
            unit=data['unit'],
            description=data.get('description', ''),
            enabled=data.get('enabled', True)
        )
        db.session.add(param)
        db.session.commit()
        return jsonify({'message': 'Parameter created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Creation failed: {str(e)}'}), 500

@internal_bp.route('/sync-parameter', methods=['PUT'])
def sync_parameter():
    """Internal endpoint to sync parameter update"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Parameter name required'}), 400
    
    try:
        param = Parameter.query.filter_by(name=data['name']).first()
        if param:
            param.unit = data.get('unit', param.unit)
            param.description = data.get('description', param.description)
            param.enabled = data.get('enabled', param.enabled)
            db.session.commit()
            return jsonify({'message': 'Parameter synced successfully'}), 200
        else:
            return jsonify({'error': 'Parameter not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500

@internal_bp.route('/sync-parameter-delete', methods=['DELETE'])
def sync_parameter_delete():
    """Internal endpoint to sync parameter deletion"""
    data = request.get_json()
    
    if not data or (not data.get('name') and not data.get('id')):
        return jsonify({'error': 'Parameter name or id required'}), 400
    
    try:
        if data.get('id'):
            param = Parameter.query.get(data['id'])
        else:
            param = Parameter.query.filter_by(name=data['name']).first()
            
        if param:
            db.session.delete(param)
            db.session.commit()
            return jsonify({'message': 'Parameter deleted successfully'}), 200
        else:
            return jsonify({'error': 'Parameter not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

@internal_bp.route('/sync-user-password', methods=['POST'])
def sync_user_password():
    """Internal endpoint to sync user password from desktop"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password_hash'):
        return jsonify({'error': 'Email and password_hash required'}), 400
    
    try:
        user = User.query.filter_by(email=data['email']).first()
        if user:
            user.password_hash = data['password_hash']
            db.session.commit()
            return jsonify({'message': 'Password synced successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500