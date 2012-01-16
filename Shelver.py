
# this module should, in some future, handle the file moving, 
# which is currently written directly in UpdateManager.py


import logging
import re
import os
import os.path
import Db

log = logging.getLogger("Shelver")

import unicodedata, string

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)

def clean_fn(filename):
  fn = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
  return ''.join(c for c in fn if c in validFilenameChars)


def get_file(episode_descriptor):

  dir = Db.get_config('completed_dir') 
  filelist = []
  for (a,b,c) in os.walk(dir):
    for f in c:
      filelist.append((f,a))

  return episode_descriptor.filter(filelist)


