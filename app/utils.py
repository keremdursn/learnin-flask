from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from app.models import Kullanici

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        kullanici_id = get_jwt_identity()
        kullanici = Kullanici.query.get(kullanici_id)

        if not kullanici or kullanici.rol != "admin":
            return jsonify({"hata": "Bu işlemi yapmaya yetkiniz yok"}), 403

        return fn(*args, **kwargs)
    return wrapper

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
