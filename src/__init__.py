from flask import Flask
from dotenv import load_dotenv
from .models import bcrypt, db
from .auth import jwt
from .routes import main_bp

def create_app():
    
    app = Flask(__name__)
    load_dotenv()
    
    app.config.from_prefixed_env()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

    # print(app.config.get("SECRET_KEY"))
    # print(app.config.get("SQLALCHEMY_DATABASE_URI"))

    bcrypt.init_app(app)
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
        
    return app