from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)


# Blueprint’leri import et
from app.users_routes import users_bp
from app.posts_routes import posts_bp
app.register_blueprint(users_bp, url_prefix='/api/kullanicilar')
app.register_blueprint(posts_bp, url_prefix='/api/gonderiler')

from app.auth_routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')

from app.comments_routes import yorum_bp
app.register_blueprint(yorum_bp, url_prefix='/api/yorum')

from app.arama_routes import arama_bp
app.register_blueprint(arama_bp, url_prefix="/api/arama")


# Modelleri import et (tablo oluşturmak için)
from app import models

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Güvenli bir anahtar belirleyin


# Veritabanını oluştur (eğer tablolar yoksa)
with app.app_context():
    db.create_all()