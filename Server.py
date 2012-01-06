import logging



import web
import json
from mimerender import mimerender
from SubscriptionManager import getSubscriptionManager
from tvdb import get_series
from Db import get_db
import Db
from UpdateManager import getUpdateManager
import urllib

log = logging.getLogger("Server")

render_xml = lambda message: '<message>%s</message>'%message
render_json = lambda **args: json.dumps(args)
render_html = lambda message: '<html><body>%s</body></html>'%message
render_txt = lambda message: message

urls = (
    r'/subscription', 'subscriptions',
    r'/subscription/(\w+)', 'subscription',
    r'/subscription/(\w+)/episodes', 'subscription_episodes',
    r'/subscription/(\w+)/(\w+)/?(.*)', 'subscription_detail',
    r'/search/(.*)', 'search',
    r'/log', 'logg',
    r'/updates', 'updates',
    r'/updates/download', 'updates_download',
    r'/updates/move', 'updates_move',
    r'/config/(\w+)', 'config_get',
    r'/config/(\w+)/(.+)', 'config_post',
    r'/html/(.*)', 'html'
)
app = web.application(urls, globals())


class subscriptions:
  def GET(self):
    return json.dumps(getSubscriptionManager().get_series())
  
class subscription:
  def GET(self, sub):
    return json.dumps(['eztv_name', 'episodes'])
  def PUT(self, sub):
    getSubscriptionManager().add_series(sub)
    return json.dumps(None)
  def DELETE(self, sub):
    getSubscriptionManager().remove_series(sub)
    return json.dumps(None)


class subscription_episodes:
  def GET(self, sub):
    return json.dumps(getSubscriptionManager().get_episodes(sub))
  def PUT(self, sub):
    return json.dumps(getSubscriptionManager().add_series(sub))

class subscription_detail:
  def GET(self, sub, field, value):
    return json.dumps(getSubscriptionManager().get_series_details(sub)[field])
  def POST(self, sub, field, value):
    getSubscriptionManager().set_series_detail(sub, field, value)
    return json.dumps(None)

class search:
  def GET(self, name):
    return json.dumps(get_series(name))

class updates:
  def GET(self):
    up = getUpdateManager()
    up.search_for_updates()
    return json.dumps(None)

class updates_download:
  def GET(self):
    up = getUpdateManager()
    up.download_new()
    return json.dumps(None)

class updates_move:
  def GET(self):
    log.warning("update_move")
    up = getUpdateManager()
    up.move_downloaded()
    return json.dumps(None)

class config_get:
  def GET(self, key):
    log.info("get config: " + key)
    return json.dumps(Db.get_config(key))

class config_post:
  def POST(self, key, value):
    Db.set_config(key, urllib.unquote(value))
    return json.dumps(None)

class logg:
  def GET(self):
    db = get_db()
    return json.dumps([ x for x in db.execute('SELECT * FROM debug') ])
class html:
  def GET(self, name):
    if not name:
      name = 'index.html'
    return open("html/" + name).read()

if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  app.run()
