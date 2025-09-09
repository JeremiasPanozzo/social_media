from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from .models import Post, Comment, User
from extension import db
import uuid
comments_bp = Blueprint('comment', __name__)

@comments_bp.route('/<uuid:post_id>/comment', methods=['POST'])
@jwt_required()
def post_comment(post_id):
    data = request.get_json()
    user_id = uuid.UUID(get_jwt_identity())
    
    content = data.get('content')
    if not content or content.strip() == "":
        return jsonify({"error": "Coment can not be empty"}), 400
    
    post = Post.find_by_id(post_id)

    if not post:
        return jsonify({"error": "Post does not exist"}), 404
    
    new_comment = Comment(user_id=user_id, content=content, post_id=post_id)

    try:
        new_comment.save()
        return jsonify({"message": "Comment created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating post", "error": str(e)}), 500
    
@comments_bp.route('/<uuid:post_id>/comments', methods=['GET'])
@jwt_required(optional=True)
def get_comments(post_id):

    post = Post.find_by_id(post_id)

    if not post:
        return jsonify({"error": "El post no existe"}), 404

    comments = Comment.find_by_post(post_id=post_id)

    return jsonify([
        {
            "id": str(c.comment_id),
            "content": c.content,
            "user": User.find_by_id(c.user_id),
            "created_at": c.created_at
        } for c in comments
    ])
