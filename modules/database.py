import os, sys, logging
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from .models import * #getting around cyclic imports

log = logging.getLogger('{0}.{1}'.format("web_api", "database"))


class Database(object):
    def __init__(self, flask_app, db_path):
        self.db_filepath = db_path
        self.flask_app = flask_app 
        self.flask_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{0}".format(db_path)
        self.flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            
        db.init_app(flask_app) 
        self.create_db_if_absent()

        self.all_appids = None
        self.all_languages = None

    
    def create_db_if_absent(self):
        
        if not os.path.isfile(self.db_filepath):
            log.info("Couldn't find db file at '{0}'. Creating it there now.".format(self.db_filepath))
            with self.flask_app.app_context():
                 db.create_all()
        else:
            log.debug("Found db file at '{0}'.".format(self.db_filepath))


    def add_app_language(self, app_id, app_name, app_pic_src, languages):
        app = self.get_app(app_id)
        if not app:
            log.debug("App '{}' ({}) doesn't exist in DB, adding it".format(app_name, app_id))
            self.add_app(app_id, app_name, app_pic_src)
            app = self.get_app(app_id)

        for name, media in languages:
            lang = self.get_lang(name, media)
            if not lang:
                log.debug("Lang '{}' - '{}' doesn't exist in DB, adding it".format(name, media))
                self.add_language_entry(name, media)
                lang = self.get_lang(name, media)


            if not self.get_app_lang_junction(app, lang):
                log.debug("Relationship between app '{}' ({}) and Lang '{}' - '{}' doesn't exist in DB, adding it".format(app_name, app_id, name, media))
                self.add_app_lang_junction(app, lang)

    def get_all_langs(self):
        with self.flask_app.app_context():
            pass

    def get_apps_with_langs(self, languages):
        apps = []
        if type(languages) is not list:
            languages = [languages]

        for lang in languages:
            with self.flask_app.app_context():
                apps += lang.apps

        return apps

    def get_lang(self, name, media):
        with self.flask_app.app_context():
            return Steam_Language.query.filter_by(language_name=name, language_presentation=media).first()

    def get_app_lang_junction(self, app, lang):
        with self.flask_app.app_context():
            return [app for app in lang.apps]

    def get_app(self, app_id):
        with self.flask_app.app_context():
            return Steam_App.query.filter_by(steam_app_id=app_id).first()

    def add_app(self, app_id, app_name, app_pic_src):
        with self.flask_app.app_context():
            db.session.add(Steam_App(
                            app_id = app_id,
                            app_name = app_name,
                            app_pic = app_pic_src))
            db.session.commit()

    def add_language_entry(self, name, media):
        with self.flask_app.app_context():
            db.session.add(Steam_Language(
                             name=name,
                             presentation=media))
            return db.session.commit()

    def add_app_lang_junction(self, app, lang):
        with self.flask_app.app_context():
            lang.apps.append(app)
            db.session.commit()