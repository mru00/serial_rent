
class TorrentProvider:
  def getTorrent(self, what):
    raise RuntimeError("subclass TorrentProvider")



def getProvider(key="EZTV"):
  if key == "EZTV":
    import TorrentProviderEZTV
    return TorrentProviderEZTV.TorrentProviderEZTV()

  raise NotImplementedError("torrent provider " + key + " not implemented")

