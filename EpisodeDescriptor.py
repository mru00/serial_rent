
# this module provides SimpleEpisodeDescriptor, 
# the class that holds the information for a specific episode
# and utility methods for it

from Shelver import clean_fn

class EpisodeDescriptor:
  pass


class SimpleEpisodeDescriptor (EpisodeDescriptor):
  def __init__ (self, tvdb_series, series_name, season_number, episode_number, meta = None):
    self.tvdb_series = tvdb_series
    self.series_name = series_name
    self.season_number = season_number
    self.episode_number = episode_number
    self._meta = meta

  def meta(self, key, default):
    if self._meta and key in self._meta.keys():
      return self._meta[key]
    return default

  def get_file_name(self, extension = "avi"):
    return clean_fn("%s S%02dE%02d %s.%s" % (self.series_name, self.season_number, self.episode_number, self.meta('episode_name', ''), extension))


  def get_query_string(self):

    return "%s S%02dE%02d" % (self.series_name, self.season_number, self.episode_number)

  def filter(self, candidates):

    sn = self.meta('eztv_name', self.series_name)
    def f1(title):
      if sn not in title.replace('.', ' '):
        return False

      patterns = [
          "S%02dE%02d" %(self.season_number, self.episode_number),
          "%dx%02d" %(self.season_number, self.episode_number)]
      return len(
          filter(lambda a: a != -1, 
            map(lambda a: title.find(a), patterns))) > 0

    return filter(lambda (t,l): f1(t), candidates)


  def __str__(self):
    return "%s[eztv:%s] / %d / %d" % (self.series_name, self.meta('eztv_name', ''), self.season_number, self.episode_number)

