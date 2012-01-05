import logging
import re
import os
import os.path
from SubscriptionManager import getSubscriptionManager

log = logging.getLogger("Shelver")

download_dir = '/home/mru/dev/06multimedia/serial_rent/torrents'
download_dir = '/home/mru/Downloads/torrentz/test'
download_dir = '/home/mru/06multimedia/serial_rent/torrents'

def get_file(episode_descriptor):

  filelist = []
  for (a,b,c) in os.walk(download_dir):
    for f in c:
      filelist.append((f,a))

  f = [ f for f in filelist if episode_descriptor.series_name in f[0].replace('.', ' ') ]
  return episode_descriptor.filter(f)
