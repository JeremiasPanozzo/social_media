from flask import Blueprint, jsonify, request, current_app, url_for, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import Post
from extension import db
from werkzeug.utils import secure_filename
import os, uuid

posts_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@posts_bp.route("/upload_post", methods=["POST"])
@jwt_required()
def create_post():
    user_id = uuid.UUID(get_jwt_identity())

    if "image" not in request.files:
        return jsonify({"message": "No image file provided"}), 400

    file = request.files["image"]
    caption = request.form.get("caption")

    if not caption or file.filename == "":
        return jsonify({"message": "Missing caption or image"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "File type not allowed"}), 400
    
    if file.filename is None:
        return jsonify({"message": "No image file provided"}), 400
    
    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    new_post = Post(caption=caption, image_path=filename, user_id=user_id)
    try:
        new_post.save()
        return jsonify({"message": "Post created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating post", "error": str(e)}), 500

@posts_bp.route('/feed', methods=['GET'])
@jwt_required()
def get_posts():
    posts = Post.find_all()
    
    result = []

    if not posts:
        return jsonify([]), 200
    
    for post in posts:
        image_url = url_for("main.uploaded_file", filename=post.image_path, _external=True)
        
        comments_data = []

        for comment in post.comments:
            comments_data.append({
                "comment_id": comment.comment_id,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "user": {
                    "user_id": comment.user.user_id,
                    "username": comment.user.username
                }
        })
            
        result.append({
            "post_id": post.post_id,
            "caption": post.caption,
            "image_path": image_url,
            "author": {
                "user_id": post.author.user_id,
                "username": post.author.username,
            },
            "comments": comments_data
        })

    return jsonify(result), 200

@posts_bp.route('/<uuid:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    post = Post.find_by_id(post_id)
    
    if post is None:
        return jsonify({"message": "Post not found"}), 404

    image_url = url_for("main.get_posts", filename=post.image_path, _external=True)
    result = {
        "post_id": post.post_id,
        "caption": post.caption,
        "image_path": image_url,
        "author": {
            "user_id": post.author.user_id,
            "username": post.author.username,
            "email": post.author.email
        }
    }

    return jsonify(result), 200

@posts_bp.route('/<uuid:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    user_id = uuid.UUID(get_jwt_identity())
    post = Post.find_by_id(post_id)

    if post is None:
        return jsonify({"message": "Post not found"}), 404

    if post.user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    # eliminar imagen del disco
    try:
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], post.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
        post.delete()
        return jsonify({"message": "Post deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error deleting post", "error": str(e)}), 500

@posts_bp.route('/<uuid:post_id>', methods=['PUT'])
@jwt_required()
def edit_post(post_id):
    user_id = get_jwt_identity()
    user_id = uuid.UUID(user_id)

    post = Post.find_by_id(post_id)

    if post is None:
        return jsonify({"message":"Post not found"}), 404
    
    if post.user_id != user_id:
        print(f"Post user: {post.user_id} y User id: {user_id}")
        return jsonify({"message":"Unauthorized"}), 403
    
    data = request.get_json()
    new_caption = data.get('caption')

    if not new_caption:
        return jsonify({"message":"Caption required"}), 400
    try:
        post.update(new_caption)
        return jsonify({"message": "Post updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating post", "error": str(e)}), 500
    
@posts_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)