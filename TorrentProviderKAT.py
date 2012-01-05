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
    #page = urllib2.urlopen("http://thepiratebay.org/search/%s/0/7/0" %(s,))
    page = open("kat_tidy.html")
    soup = BeautifulSoup(page)

    candidates = []
    r = soup.findAll('td', {'class':'torrentnameCell'})
    print r
    for i in r[0].findAll('tr'):
      print "++++"
      print i
      try:
        tds = i.findAll('td')
        td = tds[1]
        title = re.sub(r'\s+', ' ', td.div.a.string)
        title = re.sub(r'^\s*', '', title)
        title = re.sub(r'\s*$', '', title)
        
        print "title:", title
        
        magnet = tds[1].findAll('a', {'href' : re.compile('^magnet')})[0]['href']
        candidates.append( (title, magnet) )
      except Exception as ex:
        print ex
        pass

    candidates = episode_descriptor.filter(candidates)

    if len(candidates) == 0:
      raise RuntimeError("no torrent for episode '" + str(episode_descriptor) + "' found")

    episode = score(candidates)

    print episode
    return episode[1]


if __name__ == "__main__":
  logging.basicConfig(level=logging.DEBUG)
  from EpisodeDescriptor import SimpleEpisodeDescriptor
  d = SimpleEpisodeDescriptor('boardwalk empire', 2, 5)
  t = TorrentProviderTPB()
  print t.getTorrent(d)

