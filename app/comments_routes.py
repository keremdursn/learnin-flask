from flask import request, jsonify, Blueprint
from app import db
from app.models import Gonderi, Yorum
from app.schemas import YorumSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

yorum_bp = Blueprint("yorum_bp", __name__)
yorum_schema = YorumSchema()
yorumlar_schema = YorumSchema()

@yorum_bp.route("/", methods=["POST"])
@jwt_required()
def yorum_ekle():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"hata": "JSON verisi eksik"}), 400
    
    try:
        yorum = yorum_schema.load(json_data)
    except Exception as e:
        return jsonify({"hata": str(e)}), 400
    
    yorum.kullanici_id = get_jwt_identity()

    gonderi = Gonderi.query.get(yorum.gonderi_id)
    if not gonderi:
        return jsonify({"hata": "Gönderi bulunamadı"}), 404
    
    db.session.add(yorum)
    db.session.commit()
    return yorum_schema.jsonify(yorum), 201




@yorum_bp.route("/")
def gonderi_yorumlari(gonderi_id):
    yorumlar = Yorum.query.filter_by(gonderi_id=gonderi_id).all()
    return yorumlar_schema.jsonify(yorumlar)