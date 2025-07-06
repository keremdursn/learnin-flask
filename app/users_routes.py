
from flask import request, jsonify, Blueprint
from app import db
from app.models import Kullanici
from app.schemas import KullaniciSchema

users_bp = Blueprint('users_bp', __name__)

kullanici_schema = KullaniciSchema()
kullanici_list_schema = KullaniciSchema(many=True)

# Kullanıcı ekleme
@users_bp.route("", methods=["POST"])
def kullanici_ekle():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"hata": "JSON verisi eksik"}), 400
    
    try:
        yeni_kullanici = kullanici_schema.load(json_data)
    except Exception as e:
        return jsonify({"hata": str(e)}), 400
    
    
    db.session.add(yeni_kullanici)
    db.session.commit()

    return kullanici_schema.jsonify(yeni_kullanici), 201


# Kullanıcıları listeleme
@users_bp.route("", methods=["GET"])
def kullanicilari_listele():
    tum_kullanicilar = Kullanici.query.all()
    return kullanici_list_schema.jsonify(tum_kullanicilar)


# ID ye göre kullanıcı getirme
@users_bp.route("/<int:kid>", methods=["GET"])
def kullanici_getir(kid):
    kullanici = Kullanici.query.get(kid)
    if not kullanici:
        return jsonify({"hata": "Kullanıcı bulunamadı"}), 404
    return kullanici_schema.jsonify(kullanici)


# ID ye göre kullanıcı güncelleme
@users_bp.route("/<int:kid>", methods=["PUT"])
def kullanici_guncelle(kid):
    kullanici = Kullanici.query.get(kid)
    if not kullanici:
        return jsonify({"hata": "Kullanıcı bulunamadı"}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"hata": "JSON verisi eksik"}), 400
    try:
        kullanici = kullanici_schema.load(json_data, instance=kullanici, partial=True)
    except Exception as e:
        return jsonify({"hata": str(e)}), 400

    db.session.commit()
    return kullanici_schema.jsonify(kullanici)


# ID ye göre kullanıcı silme
@users_bp.route("/<int:kid>", methods=["DELETE"])
def kullanici_sil(kid):
    kullanici = Kullanici.query.get(kid)
    if not kullanici:
        return jsonify({"hata": "Kullanıcı bulunamadı"}), 404

    db.session.delete(kullanici)
    db.session.commit()
    return jsonify({"mesaj": f"{kid} ID'li kullanıcı silindi."})
