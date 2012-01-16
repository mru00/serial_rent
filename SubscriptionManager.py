
# The SubscriptionManager provides an interface to 
# the data stored in the database
#
# In future, it should also manage the notifications (new episode, download completed, ...)



import re
import logging
import tvdb
import Db

log = logging.getLogger()

class EpisodeState:
  new = "new"
  queues = "queued"
  not_found = "not_found"



class SubscriptionManager:
  def __init__(self):
    self.db = Db.get_db()

  def _make_dict(self, row):
    d = {}
    for k,v in zip(row.keys(), row):
      d[k]=v
    return d


  def add_series(self, tvdb_key, meta = None):
    if not meta:
      meta = tvdb.get_series_details(tvdb_key)

    self.db.execute('''
    insert into series 
    (tvdb_series, series_name, eztv_name)
    VALUES
    (?,?,?)''' ,(tvdb_key,meta['name'], re.sub('[tT]he (.*)', r'\1, The', meta['name'])))
    self.db.commit()

  def add_episode(self, tvdb_series, tvdb_episode, meta = None):
    try:
      if not meta:
        meta = tvdb.get_episode(tvdb_episode)
      self.db.execute('''
      insert into episodes
      (tvdb_series, 
       tvdb_episode, 
       episode_name, 
       season_number, 
       episode_number,
       aired timestamp)
      VALUES
      (?,?,?,?,?)''', (tvdb_series, tvdb_episode, meta['name'], meta['season_number'], meta['episode_number'], meta['first_aired'] ) )
      self.db.commit()
    except Exception, e:
      log.error(repr(e)+tvdb_series + "/" + tvdb_episode)

  def get_series(self):
    return map(self._make_dict, self.db.execute('''
    select * from series
    '''))

  def remove_series(self, tvdb_series):
    self.db.execute('''
    DELETE FROM series
    WHERE tvdb_series = ?''', 
    (tvdb_series,))

    self.db.execute('''
    DELETE FROM episodes
    WHERE tvdb_series = ?''', 
    (tvdb_series,))

    self.db.commit()

  def get_series_details(self, tvdb_series):
    return map(self._make_dict, self.db.execute('''
    select * from series
    WHERE tvdb_series = ?
    ''', (tvdb_series, )))[0]

  def set_series_detail(self, tvdb_series, field, value):
    assert re.match(r'\w+', field)
    self.db.execute('''
    UPDATE series
    SET ''' + field + ''' = ?
    WHERE tvdb_series = ?''',
    (value, tvdb_series))
    self.db.commit()

  def get_episodes(self, series):
    return map(self._make_dict, self.db.execute('''
    select * from episodes
    NATURAL JOIN series
    where tvdb_series = ? 
    ORDER BY season_number ASC, episode_number ASC
    ''', (series,)))


  def update_episode_state(self, series, episode, state):
    self.db.execute('''
    update episodes
    set state = ?
    where tvdb_series = ? and tvdb_episode = ?''',
    (state, series, episode))
    self.db.commit()
    


def getSubscriptionManager():
  return SubscriptionManager()



if __name__ == "__main__":
  s = getSubscriptionManager()
  archer = '110381'
  print s.get_series_details(archer)
  print s.get_episodes(arches)

