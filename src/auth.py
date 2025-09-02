from flask import Blueprint, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
from .models import User, db
from .models import RevokedToken, User

bp = Blueprint('auth', __name__)

jwt = JWTManager()

@bp.route('/register', methods=['POST'])
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

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Missing JSON in request"}), 400
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400
    
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.user_id))
    return jsonify(access_token=access_token)

@bp.route('/logout', methods=['POST'])
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

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return RevokedToken.query.filter_by(jti=jti).first() is not None
