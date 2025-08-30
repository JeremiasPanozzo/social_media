from flask import Flask
from dotenv import load_dotenv

def create_app():
    
    app = Flask(__name__)
    load_dotenv()
    
    app.config.from_prefixed_env()

    print(app.config.get("SECRET_KEY"))
    print(app.config.get("SQLALCHEMY_DATABASE_URI"))

    from .models import bcrypt, db
    
    bcrypt.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        
    return app