import logging
logging.basicConfig(level=logging.DEBUG)



import web
import json
from mimerender import mimerender
from SubscriptionManager import getSubscriptionManager
from tvdb import get_series
from Db import get_db
from UpdateManager import getUpdateManager

log = logging.getLogger("Server")

render_xml = lambda message: '<message>%s</message>'%message
render_json = lambda **args: json.dumps(args)
render_html = lambda message: '<html><body>%s</body></html>'%message
render_txt = lambda message: message

urls = (
    '/subscription', 'subscriptions',
    '/subscription/(\w+)', 'subscription',
    '/subscription/(\w+)/episodes', 'subscription_episodes',
    '/subscription/(\w+)/(\w+)/?(.*)', 'subscription_detail',
    '/search/(.*)', 'search',
    '/log', 'logg',
    '/updates', 'updates',
    '/updates/download', 'updates_download',
    '/updates/move', 'updates_move',
    '/html/(.*)', 'html'
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
    app.run()
