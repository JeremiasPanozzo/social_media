from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User, Post, RevokedToken, db

main_bp = Blueprint('main', __name__)

@main_bp.route('/hello', methods=['GET'])
def hello():
    return jsonify(message="Hello, World!")

@main_bp.route('/upload_post', methods=['POST'])
@jwt_required()
def create_posts():

    data = request.get_json()

    if not data:
        return jsonify({"message": "Missing JSON in request"}), 400

    caption = data.get("caption")
    image_path = data.get("image_path")  # más adelante podés manejar subida real

    if not caption or not image_path:
        return jsonify({"message": "Missing caption or image_path"}), 400

    user_id = get_jwt_identity()

    new_post = Post(caption=caption, image_path=image_path, user_id=user_id)
    try:
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"message": "Post created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating post", "error": str(e)}), 500

@main_bp.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    posts = Post.query.join(User).all()

    result = []
    for post in posts:
        result.append({
            "post_id": post.post_id,
            "caption": post.caption,
            "image_path": post.image_path,
            "author": {
                "user_id": post.author.user_id,
                "username": post.author.username,
                "email": post.author.email
            }
        })

    return jsonify(result), 200