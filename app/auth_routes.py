from flask import request, jsonify, Blueprint
from app import db
from app.models import Kullanici
from app.schemas import KullaniciSchema
from app.utils import send_email
from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from datetime import timedelta


auth_bp = Blueprint('auth_bp', __name__)

kullanici_schema = KullaniciSchema()
kullanici_list_schema = KullaniciSchema(many=True)


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

    # ✅ Hoş Geldin Maili Gönder
    send_email(email, "Hoş geldin!", "Kaydınız başarıyla tamamlandı.")

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


# Kullanıcının Bilgilerini Görme
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def my_profile():
    kullanici_id = get_jwt_identity()
    kullanici = Kullanici.query.get(kullanici_id)
    if not kullanici:
        return jsonify({"hata": "Kullanıcı bulunamadı"}), 404
    return kullanici_schema.jsonify(kullanici)


# Profil Güncelleme
@auth_bp.route("/me", methods=["PUT"])
@jwt_required()
def profil_guncelle():
    kullanici_id = get_jwt_identity()
    kullanici = Kullanici.query.get(kullanici_id)
    if not kullanici:
        return jsonify({"hata": "Kullanıcı bulunamadı"}), 404
    
    data = request.get_json()

    kullanici.ad = data.get("ad", kullanici.ad)
    kullanici.soyad = data.get("soyad", kullanici.soyad)

    db.session.commit()
    return jsonify({"mesaj": "Profil güncellendi!"})


# Şifre Güncelleme
@auth_bp.route("/me/password", methods=["PUT"])
@jwt_required()
def sifre_degistir():
    kullanici_id = get_jwt_identity()
    kullanici = Kullanici.query.get(kullanici_id)
    if not kullanici:
        return jsonify({"hata": "Kullanıcı bulunamadı"}), 404
    
    data = request.get_json()
    eski_sifre = data.get("eski_sifre")
    yeni_sifre = data.get("yeni_sifre")

    if not eski_sifre or not yeni_sifre:
        return jsonify({"hata": "Eski ve yeni şifre zorunludur"}), 400
    
    if not bcrypt.verify(eski_sifre, kullanici.sifre):
        return jsonify({"hata": "Eski şifre yanlış!"}), 401
    
    kullanici.sifre = bcrypt.hash(yeni_sifre)
    db.session.commit()

    return jsonify({"mesaj": "Şifre başarıyla güncellendi!"})


# Şifre sıfırlama linki isteyen endpoint (JWT token üretimi)
@auth_bp.route("/sifremi-unuttum", methods=["POST"])
def sifre_sifirlama_istegi():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"hata": "Email gereklidir"}), 400

    kullanici = Kullanici.query.filter_by(email=email).first()
    if not kullanici:
        return jsonify({"mesaj": "Eğer bu email kayıtlıysa bir bağlantı gönderildi."}), 200

    token = create_access_token(identity=kullanici.id, expires_delta=timedelta(minutes=30))
    reset_url = url_for('auth_bp.sifre_sifirla', token=token, _external=True)

    send_email(
        subject="Şifre Sıfırlama Bağlantısı",
        to=email,
        body=f"Şifrenizi sıfırlamak için tıklayın: {reset_url}"
    )

    return jsonify({"mesaj": "Eğer bu email kayıtlıysa bir bağlantı gönderildi."}), 200


# Şifre sıfırlama işlemi yapan endpoint
@auth_bp.route("/sifre-sifirla/<token>", methods=["POST"])
def sifre_sifirla(token):
    data = request.get_json()
    yeni_sifre = data.get("yeni_sifre")

    if not yeni_sifre:
        return jsonify({"hata": "Yeni şifre gereklidir"}), 400

    try:
        decoded = decode_token(token)
        kullanici_id = decoded['sub']
    except Exception:
        return jsonify({"hata": "Token geçersiz veya süresi dolmuş"}), 400

    kullanici = Kullanici.query.get(kullanici_id)
    if not kullanici:
        return jsonify({"hata": "Kullanıcı bulunamadı"}), 404

    from bcrypt import hashpw, gensalt
    hashed_password = hashpw(yeni_sifre.encode('utf-8'), gensalt())
    kullanici.password = hashed_password
    db.session.commit()

    return jsonify({"mesaj": "Şifre başarıyla güncellendi"}), 200
