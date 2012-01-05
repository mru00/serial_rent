class EpisodeDescriptor:
  pass


class SimpleEpisodeDescriptor (EpisodeDescriptor):
  def __init__ (self, series_name, season_number, episode_number, meta = None):
    self.series_name = series_name
    self.season_number = season_number
    self.episode_number = episode_number
    self.meta = meta

  def get_file_name(self):
    return "%s S%02dE%02d %s.extension" % (self.series_name, self.season_number, self.episode_number, "episodename")

  def get_query_string(self):

    return "%s S%02dE%02d" % (self.series_name, self.season_number, self.episode_number)

  def filter(self, candidates):

    def f1(title):

      patterns = [
          "S%02dE%02d" %(self.season_number, self.episode_number),
          "%dx%02d" %(self.season_number, self.episode_number)]
      return len(
          filter(lambda a: a != -1, 
            map(lambda a: title.find(a), patterns))) > 0

    return filter(lambda (t,l): f1(t), candidates)


  def __str__(self):
    try:
      ez = self.meta['eztv_name']
    except:
      ez = ''
    return "%s[eztv:%s] / %d / %d" % (self.series_name, ez, self.season_number, self.episode_number)

