
# base class for torrent providers.
# a torrent provider is a torrent tracker like 'the pirate bay', ...


class TorrentProvider():
  def getTorrent(self, what):
    raise RuntimeError("subclass TorrentProvider")



def getProvider(key="META"):
  if key == "EZTV":
    import TorrentProviderEZTV
    return TorrentProviderEZTV.TorrentProviderEZTV()
  elif key == "META":
    import TorrentProviderMeta
    return TorrentProviderMeta.TorrentProviderMeta()
  elif key == "TPB":
    import TorrentProviderTPB
    return TorrentProviderTPB.TorrentProviderTPB()


  raise NotImplementedError("torrent provider " + key + " not implemented")

