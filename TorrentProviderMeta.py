
"""
TorrentProvider that uses other torrent providers to
search for a torrent.
"""


from TorrentProvider import TorrentProvider
from TorrentProviderEZTV import TorrentProviderEZTV
from TorrentProviderTPB import TorrentProviderTPB
import logging
from traceback import format_exc

log = logging.getLogger("TorrentProviderMeta")




class TorrentProviderMeta(TorrentProvider):
  def __init__(self):

    self.providers = [
        TorrentProviderEZTV(),
        TorrentProviderTPB()
        ]

  def getTorrent(self, episode_descriptor):

    log.info("searching for " + str(episode_descriptor))

    for i in self.providers:
      try:
        t = i.getTorrent(episode_descriptor)
        if t:
          return t
      except Exception as ex:
        log.error(format_exc(ex))

    return None

