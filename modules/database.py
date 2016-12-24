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
        self._create_db_if_absent()

    def _create_db_if_absent(self):

        if not os.path.isfile(self.db_filepath):
            log.info("Couldn't find db file at '{0}'. Creating it there now.".format(self.db_filepath))
            with self.flask_app.app_context():
                 db.create_all()
        else:
            log.debug("Found db file at '{0}'.".format(self.db_filepath))

    def add_app_language(self, app_id, app_name, app_pic_src, languages):
        with self.flask_app.app_context():
            app = self._get_app(app_id)
            if not app:
                log.debug("App '{}' ({}) doesn't exist in DB, adding it".format(app_name, app_id))
                self._add_app(app_id, app_name, app_pic_src)
                app = self._get_app(app_id)

            for name, media in languages:
                lang = self._get_lang(name, media)
                if not lang:
                    log.debug("Lang '{}' - '{}' doesn't exist in DB, adding it".format(name, media))
                    self._add_language_entry(name, media)
                    lang = self._get_lang(name, media)

                if not self._does_app_have_lang(app, lang):
                    log.debug("Relationship between app '{}' ({}) and Lang '{}' - '{}' doesn't exist in DB, adding it".format(app_name, app_id, name, media))
                    self._add_lang_to_app(app, lang)

    def get_all_available_languages(self):
        with self.flask_app.app_context():
            return [(lang.id, lang.language_name, lang.language_presentation) for lang in db.session.query(Steam_Language).all()]

    def find_apps_for_language_ids(self, language_ids):
        with self.flask_app.app_context():
            apps = []
            if type(language_ids) is not list:
                language_ids = [language_ids]

            for lang in language_ids:
                with self.flask_app.app_context():
                    apps += lang.apps

            return apps

    def _get_lang(self, name, media):
        return Steam_Language.query.filter_by(language_name=name, language_presentation=media).first()

    def _does_app_have_lang(self, app, lang):
            return app in lang.apps

    def _get_app(self, app_id):
        return Steam_App.query.filter_by(steam_app_id=app_id).first()

    def _add_app(self, app_id, app_name, app_pic_src):
        db.session.add(Steam_App(
                            app_id = app_id,
                            app_name = app_name,
                            app_pic = app_pic_src))
        db.session.commit()

    def _add_language_entry(self, name, media):
        db.session.add(Steam_Language(
                             name=name,
                             presentation=media))
        db.session.commit()

    def _add_lang_to_app(self, app, lang):
        lang.apps.append(app)
        db.session.add(lang)
        db.session.commit()