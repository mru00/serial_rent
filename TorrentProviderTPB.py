import re
from TorrentProvider import TorrentProvider
from BeautifulSoup import BeautifulSoup
from EpisodeScorer import score
import urllib2, urllib
import logging
import difflib

log = logging.getLogger("TorrentProviderTPB")

class TorrentProviderTPB (TorrentProvider):
  def getTorrent(self, episode_descriptor):

    log.info("searching for torrent: %s", episode_descriptor)

    s = episode_descriptor.get_query_string()
    s = urllib.quote(s)
    log.info("searching: " + s)
    page = urllib2.urlopen("http://thepiratebay.org/search/%s/0/7/0" %(s,))
    soup = BeautifulSoup(page)

    candidates = []
    r = soup.findAll(id='searchResult')
    if len(r) == 0:
      log.info("no torrents found for query")
      return None

    for i in r[0].findAll('tr'):
      try:
        tds = i.findAll('td')
        td = tds[1]
        title = re.sub(r'\s+', ' ', td.div.a.string)
        title = re.sub(r'^\s*', '', title)
        title = re.sub(r'\s*$', '', title)
        
        magnet = tds[1].findAll('a', {'href' : re.compile('^magnet')})[0]['href']
        candidates.append( (title, magnet) )
      except Exception as ex:
        print ex
        pass

    candidates = episode_descriptor.filter(candidates)

    if len(candidates) == 0:
      log.info("no torrent candidates found")
      return None
    log.info("candidates torrents: %s" %(candidates, ))

    episode = score(candidates)
    log.info("chosen torrent: %s" %(episode, ))

    return episode[1]


if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  from EpisodeDescriptor import SimpleEpisodeDescriptor
  d = SimpleEpisodeDescriptor('boardwalk empire', 2, 5)
  t = TorrentProviderTPB()
  print t.getTorrent(d)

