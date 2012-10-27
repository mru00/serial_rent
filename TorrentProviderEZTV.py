
# Interface to EZTV.it

import re
from TorrentProvider import TorrentProvider
from BeautifulSoup import BeautifulSoup
from EpisodeScorer import score
import urllib2, urllib
import logging
import difflib
import SubscriptionManager

log = logging.getLogger("TorrentProviderEZTV")

class TorrentProviderEZTV (TorrentProvider):

  def getEZTV_series_page(self, episode_descriptor):

    subman = SubscriptionManager.getSubscriptionManager()
    
    sd = subman.get_series_details(episode_descriptor.tvdb_series)
    if sd["eztv_url"]:
      log.info("using cached eztv url: %s" % sd["eztv_url"])
      return sd["eztv_url"]

    page = urllib2.urlopen("http://eztv.it/showlist/")
    soup = BeautifulSoup(page)

    log.info("searching for torrent: %s", episode_descriptor)
    series = {}
    results = soup.findAll('tr', {"name":"hover"})
    for i in results:
      
      title =  i.a.string
      link = i.a['href']
      series[title] = link

    name = episode_descriptor.meta('eztv_name', episode_descriptor.series_name)

    cm = difflib.get_close_matches(name, series.keys())

    if len(cm) < 1:
      log.error("series " + name + " not found on eztv")
    s = series[cm[0]]
    log.info("chosen %s[%s] as series name" %(cm[0], s))

    subman.set_series_detail(episode_descriptor.tvdb_series, "eztv_url", s)
    return s

  def getTorrent(self, episode_descriptor):


    s = self.getEZTV_series_page(episode_descriptor)

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
      log.info("no torrent candidates found")
      return None
    log.info("candidate torrents %s" %(candidates,))

    episode = score(candidates)
    log.info("chosen torrent %s" %(episode,))

    return episode[1]

