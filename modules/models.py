from .database import db
from sqlalchemy import UniqueConstraint

steam_apps_langs_relationship = db.Table("steam_apps_langs", db.Model.metadata,
                                         db.Column('app_id', db.Integer, db.ForeignKey('Steam_App.id')),
                                         db.Column('lang_id', db.Integer, db.ForeignKey('Steam_Languages.id')))


class Steam_App(db.Model):
    __tablename__ = "Steam_App"
    id = db.Column(db.Integer, primary_key=True)
    steam_app_id = db.Column(db.String(10), unique=True)
    steam_app_name = db.Column(db.String(200), unique=True)
    steam_app_pic = db.Column(db.String(300))
    languages = db.relationship('Steam_Language', secondary=steam_apps_langs_relationship,
                                backref=db.backref('apps', lazy='dynamic'))

    def __init__(self, app_id, app_name, app_pic=0, languages = None):
        self.steam_app_id = app_id
        self.steam_app_name = app_name
        self.steam_app_pic = app_pic



class Steam_Language(db.Model):
    __tablename__ = "Steam_Languages"
    id = db.Column(db.Integer, primary_key=True)
    language_name = db.Column(db.String(100))
    language_presentation = db.Column(db.String(15))
    __table_args__ = (
        UniqueConstraint('language_name', 'language_presentation'),
    )

    def __init__(self, name, presentation):
        self.language_name = name
        self.language_presentation = presentation
