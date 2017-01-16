import logging, requests
from bs4 import BeautifulSoup

log = logging.getLogger('{0}.{1}'.format("web_api", "steam_parser"))

steam_app_list_url = "http://api.steampowered.com/ISteamApps/GetAppList/v0002/?format=json"
steam_app_baseurl = "http://store.steampowered.com/app"

def get_list_appids():
    '''
    Consults Steam for list of apps
    Returns a list of appids and appnames in a dict
    '''
    ret = requests.get(steam_app_list_url)
    apps = ret.json()
    apps = apps['applist']['apps']
    return apps

def get_app_info(appid):
    app_url = "{0}/{1}".format(steam_app_baseurl ,appid)
    cookie = {'birthtime': '568022401'} #some games require age validation
    r = requests.get(app_url, cookies=cookie)
    page_html = r.text
    soup = BeautifulSoup(page_html, "html5lib")
    return parse_html(soup)

def parse_html(soup):
    table = soup.find(attrs={'class': 'game_language_options'})
    rows = table.findAll('tr')
    languages = []
    for row in rows:
        cols = row.findAll('td')
        if cols:
            language_name = cols[0].text.strip()

            if cols[1].findAll('img'):
                languages.append((language_name, 'interface'))
            if cols[2].findAll('img'):
                languages.append((language_name, 'full_audio'))
            if cols[3].findAll('img'):
                languages.append((language_name, 'subtitles'))

    app_name = soup.find(attrs={'class': 'apphub_AppName'}).text
    app_pic_src = soup.find(attrs={'class': 'game_header_image_full'})['src']
    return (app_name, app_pic_src, languages)

def populate_db(db):
    apps = get_list_appids()
    log.info("Fetched {0} app ids".format(len(apps)))
    for appid, appname in ((app['appid'], app['name']) for app in apps):
        try:
            app_name, app_pic_src, languages = get_app_info(appid)
        except AttributeError as e:
            log.debug("Steam webpage for app '{0}' ({1}) could not be parsed correctly: {2}".format(appname, appid, e))
            continue
        log.debug("Found Steam app '{0}' ({1}) with languages {2}".format(appname, appid, languages))
        db.add_app_language(appid, app_name, app_pic_src, languages)

        
