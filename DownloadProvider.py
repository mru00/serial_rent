import logging

log = logging.getLogger()

class DownloadProvider:
  def enqueue(self, fn):
    raise RuntimeError("you should not invoke DownloadProvider.enqueue directly. Subclass!")


def getProvider(key="deluge"):
  if key == "deluge":
    import DownloadProviderDeluge
    return DownloadProviderDeluge.DownloadProviderDeluge()

  raise NotImplementedError("download provider " + key + " not implemented")
