import logging
import re
import os
import os.path
from SubscriptionManager import getSubscriptionManager
import Db

log = logging.getLogger("Shelver")

def get_file(episode_descriptor):

  download_dir = Db.get_config('completed_dir') 
  filelist = []
  for (a,b,c) in os.walk(download_dir):
    for f in c:
      filelist.append((f,a))

  f = [ f for f in filelist if episode_descriptor.series_name in f[0].replace('.', ' ') ]
  return episode_descriptor.filter(f)
