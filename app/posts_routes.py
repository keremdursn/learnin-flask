from flask import request, jsonify, Blueprint, current_app
from app import db
from app.models import Gonderi
from app.schemas import GonderiSchema
from app.utils import admin_required, allowed_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os

posts_bp = Blueprint('posts_bp', __name__)

gonderi_schema = GonderiSchema()
gonderi_list_schema = GonderiSchema(many=True)


# Gönderi ekleme
@posts_bp.route("", methods=["POST"])
def gonderi_ekle():
    Kullanici_id = get_jwt_identity()

    json_data = request.get_json()
    if not json_data:
        return jsonify({"hata": "JSON verisi eksik"}), 400

    try:
        yeni = gonderi_schema.load(json_data)
    except Exception as e:
        return jsonify({"hata": str(e)}), 400
    
    
    
    yeni.kullanici_id = Kullanici_id

    
    db.session.add(yeni)
    db.session.commit()

    return gonderi_schema.jsonify(yeni), 201


# Gönderileri listeleme
@posts_bp.route("", methods=["GET"])
def gonderileri_listele():
    tum_gonderiler = Gonderi.query.all()
    return gonderi_list_schema.jsonify(tum_gonderiler)


# Sorguyla gönderi listeleme
@posts_bp.route("", methods=["GET"])
def sorgulu_gonderi_listele():
    # Query string parametrelerini al
    kullanici_id = request.args.get("kullanici_id", type=int)
    aranan = request.args.get("aranan", type=str)
    orderby = request.args.get("orderby", default="created_at")
    order = request.args.get("order", default="desc")
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=5, type=int)

    # Sorguyu başlat
    sorgu = Gonderi.query
    
    if kullanici_id:
        sorgu = sorgu.filter_by(kullanici_id=kullanici_id)
    if aranan:
        sorgu = sorgu.filter(
            Gonderi.baslik.ilike(f"%{aranan}%") | Gonderi.icerik.ilike(f"%{aranan}%")
        )

    siralama_kriteri = getattr(Gonderi, orderby, Gonderi.created_at)
    if order == "desc":
        sorgu = sorgu.order_by(siralama_kriteri.desc())
    else:
        sorgu = sorgu.order_by(siralama_kriteri)
    
    sayfa = sorgu.paginate(page=page, per_page=per_page, error_out=False)

    return gonderi_list_schema.jsonify(sayfa.items)


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


# Gönderiye Resim Yükleme Endpoint’i
@posts_bp.route("/<int:gid>/resim", methods=["POST"])
@jwt_required()
def gonderi_resim_ekle(gid):
    gonderi = Gonderi.query.get(gid)
    if not gonderi:
        return jsonify({"hata": "Gönderi bulunamadı"}), 404

    kullanici_id = get_jwt_identity()
    if gonderi.kullanici_id != kullanici_id:
        return jsonify({"hata": "Bu gönderiye resim yükleyemezsiniz"}), 403

    if 'dosya' not in request.files:
        return jsonify({"hata": "Dosya alanı eksik"}), 400

    dosya = request.files['dosya']

    if dosya.filename == '':
        return jsonify({"hata": "Dosya seçilmedi"}), 400

    if dosya and allowed_file(dosya.filename):
        filename = secure_filename(dosya.filename)
        yol = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        dosya.save(yol)

        # Resim URL'si olarak path'i kaydet (basit örnek)
        gonderi.resim_url = f"/uploads/{filename}"
        db.session.commit()

        return jsonify({"mesaj": "Resim yüklendi", "url": gonderi.resim_url}), 200

    return jsonify({"hata": "Geçersiz dosya formatı"}), 400



@posts_bp.route("/admin-temizle", methods=["DELETE"])
@jwt_required()
@admin_required
def tum_gonderileri_temizle():
    from app.models import Gonderi
    Gonderi.query.delete()
    db.session.commit()
    return jsonify({"mesaj": "Tüm gönderiler silindi!"})