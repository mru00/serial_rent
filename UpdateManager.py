
# this module provides the methods to
#  * search for new torrents
#  * download those torrents
#  * move the files to get a nice sorted file archive
#
# this means that basically this module glues everything together

import logging
import SubscriptionManager
import tvdb
import DownloadProvider, TorrentProvider
from EpisodeDescriptor import SimpleEpisodeDescriptor
from Shelver import get_file, clean_fn
import os
import Db
import shutil
from traceback import format_exc


log = logging.getLogger('UpdateManager')

class UpdateManager():
  def __init__(self):
    self.subs = SubscriptionManager.getSubscriptionManager()

  def search_for_updates(self):
    series = [ x['tvdb_series'] for x in self.subs.get_series() ]
    for i in series:
      tvdb_data = tvdb.get_series_all(i, banners=False, actors=False)
      episodes = [ x['tvdb_episode'] for x in self.subs.get_episodes(i) ]
      new_episodes = [ e for e in tvdb_data['episodes'] if e['id'] not in episodes ]
      for e in new_episodes:
        self.subs.add_episode(i, e['id'], e)

  def download_new(self):
    dl = DownloadProvider.getProvider()
    to = TorrentProvider.getProvider()

    for series in self.subs.get_series():
      for episode in self.subs.get_episodes(series['tvdb_series']):
        series_name = series['series_name']
        season_number = episode['season_number']
        episode_number = episode['episode_number']

        if episode['state'] != "new":
          continue

        try:
          ds = SimpleEpisodeDescriptor(series_name, 
              int(season_number), 
              int(episode_number), episode)

          try:
            magnet = to.getTorrent(ds)
            if not magnet:
              raise RuntimeError("episode not found: " + str(ds))
          except Exception as ex:
            self.subs.update_episode_state(episode['tvdb_series'], 
                episode['tvdb_episode'], 
                "no torrent found")
            raise

          try:
            dl.enqueue(magnet)
          except Exception as ex:
            self.subs.update_episode_state(episode['tvdb_series'], 
                episode['tvdb_episode'], 
                "failed to enqueue")
            raise

          self.subs.update_episode_state(episode['tvdb_series'], 
              episode['tvdb_episode'], 
              "enqueued")

        except Exception as ex:

          log.warn("failed to enqueue %s/%s/%s: %s" % (series_name, season_number, episode_number, format_exc(ex)))


  def move_downloaded(self):

    log.info("move_downloaded")
    dl = DownloadProvider.getProvider()
    to = TorrentProvider.getProvider()

    for series in self.subs.get_series():
      for episode in self.subs.get_episodes(series['tvdb_series']):
        series_name = series['series_name']
        season_number = episode['season_number']
        episode_number = episode['episode_number']

        if episode['state'] != "enqueued":
          continue

        ds = SimpleEpisodeDescriptor(series_name, 
              int(season_number), 
              int(episode_number), episode)
        try:

          f = get_file(ds)

          if len(f) == 1:
            log.info("found file for %s: %s" %(str(ds), repr(f)))
          else:
            raise RuntimeError("file not found")


          # pick first element of result array as file.
          # result will contain only one element anyhow
          f = f[0]

          targetdir = Db.get_config('sorted_dir')
          targetdir = os.path.join(targetdir, clean_fn(series_name), "Season %d" %(season_number,))
          if not os.path.isdir(targetdir):
            os.makedirs(targetdir)

          log.info("created directory")
          extension = os.path.splitext(f[0])[1][1:]
          src = os.path.join(f[1], f[0])
          dst = os.path.join(targetdir, ds.get_file_name(extension))
          log.info("moving file %s to %s" % (src, dst))
          shutil.move(src, dst)

          self.subs.update_episode_state(episode['tvdb_series'], 
              episode['tvdb_episode'], 
              "done")

        except Exception as ex:

          log.warn("failed to find file for %s/%s/%s: %s" % (series_name, season_number, episode_number, format_exc(ex)))

def getUpdateManager():
  return UpdateManager()


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  u = UpdateManager()
  u.search_for_updates()
  u.download_new()

