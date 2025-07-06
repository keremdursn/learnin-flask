from flask import request, jsonify, Blueprint
from app import db
from app.models import Kullanici, Gonderi
from app.schemas import GonderiSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


posts_bp = Blueprint('posts_bp', __name__)

gonderi_schema = GonderiSchema()
gonderi_list_schema = GonderiSchema(many=True)


# Gönderi ekleme
@posts_bp.route("", methods=["POST"])
def gonderi_ekle():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"hata": "JSON verisi eksik"}), 400

    try:
        yeni = gonderi_schema.load(json_data)
    except Exception as e:
        return jsonify({"hata": str(e)}), 400
    
    
    Kullanici_id = get_jwt_identity()
    yeni.kullanici_id = Kullanici_id
    
    db.session.add(yeni)
    db.session.commit()

    return gonderi_schema.jsonify(yeni), 201


# Gönderileri listeleme
@posts_bp.route("", methods=["GET"])
def gonderileri_listele():
    tum_gonderiler = Gonderi.query.all()
    return gonderi_list_schema.jsonify(tum_gonderiler)


# ID ye göre gönderi getirme
@posts_bp.route("/<int:gid>", methods=["GET"])
def gonderi_getir(gid):
    gonderi = Gonderi.query.get(gid)
    if not gonderi:
        return jsonify({"hata": "Gönderi bulunamadı"}), 404
    return gonderi_schema.jsonify(gonderi)


# ID ye göre gönderi güncelleme
@posts_bp.route("/<int:gid>", methods=["PUT"])
def gonderi_guncelle(gid):
    gonderi = Gonderi.query.get(gid)
    if not gonderi:
        return jsonify({"hata": "Gönderi bulunamadı"}), 404
    
    if gonderi.kullanici_id != get_jwt_identity():
        return jsonify({"hata": "Bu gönderi size ait değil"}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({"hata": "JSON verisi eksik"}), 400
    
    try:
        guncellenen_gonderi = gonderi_schema.load(json_data, instance=gonderi, partial=True)
    except Exception as e:
        return jsonify({"hata": str(e)}), 400

    db.session.commit()
    return gonderi_schema.jsonify(guncellenen_gonderi)


# ID ye göre gönderi silme
@posts_bp.route("/<int:gid>", methods=["DELETE"])
def gonderi_sil(gid):
    gonderi = Gonderi.query.get(gid)
    if not gonderi:
        return jsonify({"hata": "Gönderi bulunamadı"}), 404
    
    # Sadece gönderi sahibi silebilir
    if gonderi.kullanici_id != get_jwt_identity():
        return jsonify({"hata": "Bu gönderi size ait değil"}), 403

    db.session.delete(gonderi)
    db.session.commit()
    return jsonify({"mesaj": "Gönderi silindi"}), 204


# Kullanıcıya ait gönderileri listeleme
@posts_bp.route("/kullanici/me", methods=["GET"])
@jwt_required()
def kendi_gonderilerim():
    kullanici_id = get_jwt_identity()

    gonderiler = Gonderi.query.filter_by(kullanici_id=kullanici_id).all()
    
    return gonderi_list_schema.jsonify(gonderiler)
