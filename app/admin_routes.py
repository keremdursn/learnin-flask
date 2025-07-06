from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.utils import admin_required
from app import db
from app.models import Kullanici, Gonderi
from app.schemas import KullaniciSchema, GonderiSchema

admin_bp = Blueprint("admin_bp", __name__)

kullanici_schema = KullaniciSchema()
kullanici_list_schema = KullaniciSchema(many=True)

gonderi_schema = GonderiSchema()
gonderi_list_schema = GonderiSchema(many=True)


# Tüm Kullanıcıları Listeleme
@admin_bp.route("/kullanicilar", methods=["GET"])
@jwt_required()
@admin_required
def tum_kullanicilari_listele():
    kullanicilar = Kullanici.query.all()

    return kullanici_list_schema.jsonify(kullanicilar)


# Kullanıcı Silme
@admin_bp.route("/kullanicilar/<int:uid", methods=["DELETE"])
@jwt_required()
@admin_required
def kullanici_sil(uid):
    kullanici = Kullanici.query.get(uid)
    if not kullanici:
        return jsonify({"hata": "Kullanici Bulunamadi."}), 404
    
    db.session.delete(kullanici)
    db.session.commit()

    return jsonify({"mesaj": "Kullanici silindi."}), 204


# Tüm Gönderileri Listeleme
@admin_bp.route("/gonderiler", methods=["GET"])
@jwt_required()
@admin_required
def tum_gonderileri_listele():
    gonderiler = Gonderi.query.all()

    return gonderi_list_schema.jsonify(gonderiler)


# Admin – Gönderi Silme
@admin_bp.route("/gonderiler/<int:gid", methods=["DELETE"])
@jwt_required()
@admin_required
def gonderi_sil(gid):
    gonderi = Gonderi.query.get(gid)
    if not gonderi:
        return jsonify({"hata": "Gönderi bulunamadı"}), 404
    
    db.session.delete(gonderi)
    db.session.commit()
    
    return jsonify({"mesaj": "Gönderi silindi"}), 204