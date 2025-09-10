from typing import Any
from extension import db, bcrypt
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(db.Model):

    """User model."""
    
    __tablename__ = 'users'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Relation 1:N
    posts = db.relationship('Post', backref='author', cascade='all, delete-orphan')
    # Relation 1:N
    comments = db.relationship('Comment', backref='user', cascade='all, delete-orphan')

    def __init__(self, username, email, password):
        """User model constructor."""
        self.username = username
        self.email = email
        self.set_password(password)

    def check_password(self, password):
        """Check user's password."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_password(self, password):
        """Set user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    @classmethod
    def find_by_username(cls, username):
        """Find a user by username."""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    def update(self, **data):
        """Update allowed fields of user"""
        allowed_fields = {"username", "email"}
        for field, value in data.items():
            if field in allowed_fields:
            # Evitar que se repita username o email
                if field == "username":
                    existing = User.query.filter_by(username=value).first()
                    if existing and existing.user_id != self.user_id:
                        raise ValueError("Username already taken")
                if field == "email":
                    existing = User.query.filter_by(email=value).first()
                    if existing and existing.user_id != self.user_id:
                        raise ValueError("Email already taken")

            setattr(self, field, value)
        db.session.commit()

    def save(self):
        """Save the user to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the user from the database."""
        db.session.delete(self)
        db.session.commit()

class Post(db.Model):

    """Post model."""

    __tablename__ = 'posts'

    post_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    caption = db.Column(db.String(200), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    # Relation 1:N
    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan')

    def __init__(self, caption, image_path, user_id):
        """Post model constructor."""
        self.caption = caption
        self.image_path = image_path
        self.user_id = user_id

    def save(self):
        """Save the post to the database."""
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Delete the post to the database"""
        db.session.delete(self)
        db.session.commit()
    
    def update(self, new_caption):
        """Update allowed fields of the post."""
        self.caption = new_caption
        db.session.commit()

    @classmethod
    def find_by_user(cls, user_id):
        """Find posts by user ID."""
        return cls.query.filter_by(user_id=user_id).all()
    
    @classmethod
    def find_by_id(cls, post_id):
        """Find a post by ID."""
        return cls.query.filter_by(post_id=post_id).first()
    
    @classmethod
    def find_all(cls):
        """Find all posts"""
        return cls.query.all()
    
    @classmethod
    def find_all_comment(cls, post_id):
        post = cls.query.get(post_id)
        if post:
            return post.comments
        return []

class Comment(db.Model):
    __tablename__ = 'comments'

    comment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    user_id = db.Column(db.ForeignKey('users.user_id'), nullable=False)
    post_id = db.Column(db.ForeignKey('posts.post_id'), nullable=False)

    def __init__(self, content, user_id, post_id):
        self.content = content
        self.user_id = user_id
        self.post_id = post_id

    def save(self):
        """Save the comment to the database."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_post(cls, post_id):
        return cls.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    

class RevokedToken(db.Model):

    """Revoked Token model."""
    
    __tablename__ = "revoked_tokens"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    jti = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, jti):
        self.jti = jti