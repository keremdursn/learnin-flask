# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from app.config import Config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Genişletici modülleri initialize et
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # Blueprint'leri import ve register et
    from app.users_routes import users_bp
    from app.posts_routes import posts_bp
    from app.auth_routes import auth_bp
    from app.comments_routes import yorum_bp
    from app.arama_routes import arama_bp
    from app.admin_routes import admin_bp
    from app.error_handlers import register_error_handlers

    app.register_blueprint(users_bp, url_prefix='/api/kullanicilar')
    app.register_blueprint(posts_bp, url_prefix='/api/gonderiler')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(yorum_bp, url_prefix='/api/yorum')
    app.register_blueprint(arama_bp, url_prefix="/api/arama")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # Global error handlers
    register_error_handlers(app)

    # Uploads klasörü için dosya servisi
    from flask import send_from_directory
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Veritabanı tablolarını oluştur
    with app.app_context():
        db.create_all()

    return app
