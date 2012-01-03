import logging
import SubscriptionManager
import tvdb
import DownloadProvider, TorrentProvider
from EpisodeDescriptor import SimpleEpisodeDescriptor


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
        series_name = series['name']
        season_number = episode['season_number']
        episode_number = episode['episode_number']

        if episode['state'] != "new":
          continue

        try:
          ds = SimpleEpisodeDescriptor(series_name, 
              int(season_number), 
              int(episode_number), series)

          try:
            magnet = to.getTorrent(ds)
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

          log.warn("failed to enqueue %s/%s/%s: %s" % (series_name, season_number, episode_number, repr(ex)))



def getUpdateManager():
  return UpdateManager()


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  u = UpdateManager()
  u.search_for_updates()
  u.download_new()

