from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User
from extension import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    """Get login user information."""
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    result = {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
    }

    return jsonify(result), 200


@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user_info():
    """Update login user information."""
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)

    if user is None:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()

    try:
        user.update(**data)
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating user info", "error": str(e)}), 500

    return jsonify({"message": "User info updated"}), 200

@users_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_current_user_account():
    """Delete login user account."""
    user_id = get_jwt_identity()
    user = User.find_by_id(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    try:
        user.delete()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting user account", "error": str(e)}), 500

    return jsonify({"message": "User account deleted"}), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    """Get user information by user ID."""
    user = User.find_by_id(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    result = {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
    }

    return jsonify(result), 200