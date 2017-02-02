from flask import Flask, request
from modules.database import Database
from modules.config import get_config
import sys, os, logging, json
application = Flask("steam-language-filter")

logging.basicConfig()
log = logging.getLogger('web_api')
log.setLevel(logging.INFO)
fh = logging.FileHandler('web_api.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


config_filename = "web_api.config"
config_path = "{0}/{1}".format(os.path.dirname(os.path.realpath(__file__)), config_filename)

default_db_filename = "web_api.sql"
db_path = "{0}/{1}".format(os.path.dirname(os.path.realpath(__file__)), default_db_filename)

default_log_level = "DEBUG"


config = get_config(config_path, db_path, default_log_level)

log.setLevel(config['log_level'])
db = Database(application, config['db_filepath'])


@application.route('/api/v1/get_languages/')
def get_languages():
    languages = db.get_all_available_languages()
    return json.dumps(languages)

@application.route('/api/v1/get_apps/<csv_list_of_language_ids>/<start_index>/<end_index>')
def get_apps(csv_list_of_language_ids, start_index, end_index):
    try:
        language_ids = csv_list_of_language_ids.split(",")
        language_ids = [int(id.strip()) for id in language_ids]
    except Exception as e:
        log.error("Exception for first positional argument (`csv_list_of_language_ids`) for GET request: {0}".format(e))
        return "Invalid value for first positional argument (`csv_list_of_language_ids`)"

    try:
        start_index = int(start_index.strip())
        if start_index < 0:
            raise ValueError("Expecting start_index to be greater than 0")

    except Exception as e:
        log.error("Exception for second positional argument (`start_index`) for GET request: {0}".format(e))
        return "Invalid value for second positional argument (`start_index`)"

    try:
        end_index = int(end_index.strip())
        if end_index <= start_index:
            raise ValueError("Expecting end_index to be greater than start_index")
    except Exception as e:
        log.error("Exception for third positional argument (`end_index`) for GET request: {0}".format(e))
        return "Invalid value for third positional argument (`end_index`)"

    apps = db.find_apps_for_language_ids(language_ids, start_index, end_index)
    apps = [{"steam_app_id": app.steam_app_id, "steam_app_name": app.steam_app_name, "steam_app_pic": app.steam_app_pic} for app in apps]
    return json.dumps(apps)

if __name__ == "__main__":
        application.run(host='0.0.0.0', port=8080, debug=True)
