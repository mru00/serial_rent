import logging
import sqlite3
import time
import logging.handlers

db = None

def get_db():
    db =sqlite3.connect('subscriptions.db')
    db.row_factory =sqlite3.Row
   
    db.execute('''
    create table 
     if not exists 
      series
      (tvdb_series text,
       name text,
       eztv_name text,
       added timestamp DEFAULT CURRENT_TIMESTAMP, 
       PRIMARY KEY(tvdb_series)
      )
    ''');

    db.execute('''
    create table 
     if not exists
      episodes
       (tvdb_series integer,
        tvdb_episode integer,
        season_number integer,
        episode_number integer,
        name text,
        torrent_name text,
        filename text, 
        added timestamp DEFAULT CURRENT_TIMESTAMP,
        state text DEFAULT "new",
        PRIMARY KEY(tvdb_series, tvdb_episode)
       )
    ''')

    db.execute("CREATE TABLE IF NOT EXISTS debug(date text, loggername text, srclineno integer, func text, level text, msg text)")

    db.commit()

    return db


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


logging.basicConfig()
#logging.getLogger().addHandler(SQLiteHandler())



