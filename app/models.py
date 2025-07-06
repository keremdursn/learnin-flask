from app import db
from datetime import datetime

class Kullanici(db.Model):
    __tablename__ = "kullanici"

    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    sifre = db.Column(db.String(128), nullable=False)

    gonderiler = db.relationship("Gonderi", backref="kullanici", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "ad": self.ad,
            "soyad": self.soyad,
            "email": self.email,
            "gonderiler" : [g.id for g in self.gonderiler]
        }
    

class Gonderi(db.Model):
    __tablename__ = "gonderi"

    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(100), nullable=False)
    icerik = db.Column(db.Text, nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    rol = db.Column(db.String(20), default="user")  # varsayılan rol
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "baslik": self.baslik,
            "icerik": self.icerik,
            "kullanici_id": self.kullanici_id
        }
    
class Yorum(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    icerik = db.Column(db.Text, nullable=False)

    kullanici_id = db.Column(db.Integer, db.ForeignKey("kullanici.id"), nullable=False)
    gonder_id = db.Column(db.Integer, db.ForeignKey("gonderi.id"), nullable=False)
                          
    kullanici = db.relationship("Kullanici", backref="yorumlar")
    gonderi = db.relationship("Gonderi", backref="yorumlar")