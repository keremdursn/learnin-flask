from app.models import Kullanici, Gonderi, Yorum
from app import ma
from marshmallow import fields

class KullaniciSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Kullanici
        load_instance = True

    id = ma.auto_field()    
    ad = ma.Str(required=True)
    soyad = ma.Str(required=True)
    email = ma.Email(required=True)

class KullaniciPublicSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Kullanici

    id = fields.Int()
    ad = fields.Str()
    soyad = fields.Str()

class GonderiSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Gonderi
        load_instance = True

    id = ma.auto_field()
    baslik = ma.Str(required=True)
    icerik = ma.Str(required=True)
    kullanici_id = fields.Integer(dump_only=True)

    Kullanici = fields.Nested(KullaniciPublicSchema)
    
class YorumSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Yorum
        load_instance = True

    id = ma.auto_field()
    icerik = ma.Str(required=True)
    gonderi_id = fields.Integer(required=True)
    kullanici_id = fields.Integer(dump_only=True)
    
    Kullanici = fields.Nested(KullaniciPublicSchema)



    