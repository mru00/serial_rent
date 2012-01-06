import logging
import sqlite3
import time
import logging.handlers

db = None


def update_schema(db):
  def v0():
    db.execute('''
    create table 
      series
      (tvdb_series text,
       series_name text,
       eztv_name text,
       series_added timestamp DEFAULT CURRENT_TIMESTAMP, 
       PRIMARY KEY(tvdb_series)
      )
    ''');

    db.execute('''
    create table 
      episodes
       (tvdb_series integer,
        tvdb_episode integer,
        season_number integer,
        episode_number integer,
        episode_name text,
        torrent_name text,
        filename text, 
        episode_added timestamp DEFAULT CURRENT_TIMESTAMP,
        state text DEFAULT "new",
        PRIMARY KEY(tvdb_series, tvdb_episode)
       )
    ''')

    db.execute("CREATE TABLE IF NOT EXISTS debug(date text, loggername text, srclineno integer, func text, level text, msg text)")


    db.execute('''
    CREATE TABLE 
     config
      (download_dir text, 
       completed_dir text, 
       sorted_dir text
      )''')

    db.execute('''
    INSERT INTO config
    (download_dir)
    VALUES (NULL)
    ''')


  updates = [v0]

  r = db.execute('''
    SELECT version
    FROM schema_version
    ''')
  v = r.fetchone()['version']

  while v < len(updates):
    updates[v]()
    v += 1
    db.execute('''
      UPDATE schema_version
      SET version = ?''', (v,))
    db.commit()


def get_db():
    db =sqlite3.connect('subscriptions.db')
    db.row_factory =sqlite3.Row
  
    db.execute('''
    CREATE TABLE 
     IF NOT EXISTS
      schema_version
      (version INTEGER DEFAULT 0)
      ''');
    r = db.execute('''
    SELECT COUNT(*) as c
    FROM schema_version
    ''')
    if r.fetchone()['c'] == 0:
      db.execute('''
      INSERT INTO 
      schema_version
      VALUES (0)''')

    db.commit()
    update_schema(db)


    return db

def as_dict(rows):
  def _md(row):
    d = {}
    for k,v in zip(row.keys(), row):
      d[k]=v
    return d

  return map(_md, rows)

def get_config(key):
  r = as_dict(get_db().execute('''
  SELECT * FROM
  config
  '''))
  return r[0][key]

def set_config(key, value):
  db = get_db()
  
  db.execute('''
  UPDATE config
  SET ''' + key + ''' = ?''', (value,))
  db.commit()


class SQLiteHandler(logging.Handler): # Inherit from logging.Handler
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        self.db = get_db()
        # record.message is the log message
        thisdate = time.time()
        print record.getMessage()
        self.db.execute('INSERT INTO debug(date, loggername, srclineno, func, level, msg) VALUES(?,?,?,?,?,?)', (thisdate, record.name, record.lineno, record.funcName, record.levelname, record.msg))
        self.db.commit()


if __name__ == "__main__":
  logging.basicConfig()
  #logging.getLogger().addHandler(SQLiteHandler())



