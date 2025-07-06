from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from app.models import Gonderi
from app.schemas import GonderiSchema

arama_bp = Blueprint("arama_bp", __name__)
gonderi_schema = GonderiSchema()
gonderi_list_schema = GonderiSchema(many=True)

@arama_bp.route("", methods=["GET"])
def arama_yap():
    aranan = request.args.get("aranan", type=str)
    kullanici_id = request.args.get("kullanici_id", type=int)

    # baslikta = request.args.get("baslikta", default="true") == "true"
    # icerikte = request.args.get("icerikte", default="true") == "true"
    

    # Sorguya başla
    sorgu = Gonderi.query

    # kosullar = []
    # if baslikta:
    #     kosullar.append(Gonderi.baslik.ilike(f"%{kelime}%"))
    # if icerikte:
    #     kosullar.append(Gonderi.icerik.ilike(f"%{kelime}%"))

    # # Arama filtresi
    # if kosullar:
    #     sorgu = sorgu.filter(or_(*kosullar))

    if kullanici_id:
        sorgu = sorgu.filter_by(kullanici_id=kullanici_id)
    if aranan:
        sorgu = sorgu.filter(
            Gonderi.baslik.ilike(f"%{aranan}%") | Gonderi.icerik.ilike(f"%{aranan}%")
        )

    sonuc = sorgu.order_by(Gonderi.created_at.desc()).all()
    return gonderi_list_schema.jsonify(sonuc)
