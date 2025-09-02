from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from .models import User
from .models import RevokedToken, User
from extension import db, jwt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Missing JSON in request"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not password or not email:
        return jsonify({"message": "Missing username or password or email"}), 400

    existing_user = User.find_by_username(username)
    
    if existing_user:
        return jsonify({"message": "User already exists"}), 400
    
    new_user = User(username, email, password)

    try:
        new_user.save()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating user"}), 500
    
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Missing JSON in request"}), 400
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400
    
    user = User.find_by_username(username)

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))

    return jsonify({"access_token": access_token, "refresh_token": refresh_token})

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    try:
        revoked_token = RevokedToken(jti)
        db.session.add(revoked_token)
        db.session.commit()
        return jsonify({"message": "Successfully logged out"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to log out'}), 500

## Errors token handlers ##
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return RevokedToken.query.filter_by(jti=jti).first() is not None

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return jsonify({"message": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Invalid token", "error": str(error)}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Request does not contain an access token", "error": str(error)}), 401