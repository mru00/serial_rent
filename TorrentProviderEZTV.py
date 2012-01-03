import re
from TorrentProvider import TorrentProvider
from BeautifulSoup import BeautifulSoup
from EpisodeScorer import score
import urllib2, urllib
import logging
import difflib

log = logging.getLogger("TorrentProviderEZTV")

class TorrentProviderEZTV (TorrentProvider):
  def getTorrent(self, episode_descriptor):

    page = urllib2.urlopen("http://eztv.it/showlist/")
    soup = BeautifulSoup(page)

    log.info("searching for torrent: %s", episode_descriptor)
    series = {}
    results = soup.findAll('tr', {"name":"hover"})
    for i in results:
      
      title =  i.a.string
      link = i.a['href']
      series[title] = link
      #log.info("possible torrent: %s/%s" % (title, link))


    name = None
    try:
      name = episode_descriptor.meta['eztv_name']
    except Exception as ex:
      name = episode_descriptor.series_name
      log.info("no eztv name for %s, error: %s" %(episode_descriptor.series_name, repr(ex)))


    cm = difflib.get_close_matches(name, series.keys())

    log.info("after filer: " + repr(cm))
    if len(cm) < 1:
      log.error("series " + name + " not found on eztv")
    s = series[cm[0]]
    log.info("chosen " + s + " as series name")

    page = urllib2.urlopen("http://eztv.it" + s)
    soup = BeautifulSoup(page)

    candidates = []
    for result in soup.findAll('tr', {"class":"forum_header_border"}):
      parts = result.findAll('td', {"class":"forum_thread_post"})
      if len(parts) != 4:
        continue
      title = parts[1].a.string
      magnet = parts[2].findAll('a', {"class":"magnet"})[0]['href']

      candidates.append( (title, magnet) )

    candidates = episode_descriptor.filter(candidates)

    if len(candidates) == 0:
      raise RuntimeError("no torrent for episode '" + str(episode_descriptor) + "' found")

    episode = score(candidates)

    print episode
    return episode[1]

