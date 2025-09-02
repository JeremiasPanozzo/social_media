from flask import Blueprint, jsonify, request, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import Post
from extension import db
from werkzeug.utils import secure_filename
import os

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route("/upload_post", methods=["POST"])
@jwt_required()
def create_post():
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
    
    filename = secure_filename(file.filename)
    
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    user_id = get_jwt_identity()

    new_post = Post(caption=caption, image_path=filename, user_id=user_id)
    try:
        new_post.save()
        return jsonify({"message": "Post created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating post", "error": str(e)}), 500

@main_bp.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    user_id = get_jwt_identity()
    posts = Post.find_by_user(user_id)

    result = []
    for post in posts:
        image_url = url_for("main.get_posts", filename=post.image_path, _external=True)
        result.append({
            "post_id": post.post_id,
            "caption": post.caption,
            "image_path": image_url,
            "author": {
                "user_id": post.author.user_id,
                "username": post.author.username,
                "email": post.author.email
            }
        })

    return jsonify(result), 200