from flask import request, jsonify, Blueprint
from app import db
from app.models import Kullanici
from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth_bp', __name__)


# 👤 KAYIT ENDPOINTİ
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    
    existing_user = Kullanici.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400
    
    hashed_password = bcrypt.hash(password)

    new_user = Kullanici(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# 🔑 GİRİŞ ENDPOINTİ
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    
    user = Kullanici.query.filter_by(email=email).first()
    if not user or not bcrypt.verify(password, user.password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity={"id": user.id, "email": user.email})
    
    return jsonify({"access_token": access_token}), 200

# 🔒 KORUNAN ENDPOINT ÖRNEĞİ
@auth_bp.route("/profil", methods=["GET"])
@jwt_required()
def profil():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Welcome {current_user['email']}!"}), 200

