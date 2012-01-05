import logging
if __name__ == "__main__":
  logging.basicConfig(level = logging.DEBUG)


from DownloadProvider import DownloadProvider
from multiprocessing import Process, Queue
import Db

log = logging.getLogger("DownloadProviderDeluge")

from deluge.ui.client import client
from deluge.log import setupLogger
setupLogger()


def _run_deluge(fun, *args):
  def _wrap(queue, *args):

    from twisted.internet import reactor
    res = fun(reactor, *args)
    reactor.run()
    queue.put(res)

  q = Queue()
  p = Process(target = _wrap, args = (q,) + args)
  p.start()
  p.join()

  return q.get()


class DownloadProviderDeluge (DownloadProvider):
  def __init__(self):
    pass

  def enqueue(self, fn):

    download_dir = Db.get_config("download_dir")
    completed_dir = Db.get_config("completed_dir")
    
    # TODO: mkdir completed, download

    print "dl: ", download_dir
    print "cm: ", completed_dir

    def run(reactor, fn):
      global new_id

      log.info("should download " + str(fn))
      d = client.connect()
      reactor.resi = 5
      result = 5
      new_id = 5


      def on_set_1(new_id, result):
        c = client.core.set_torrent_move_completed(new_id, True)
        c.addCallback(lambda a:on_set_2(new_id, a))
        c.addErrback(on_add_fail)

      def on_set_2(new_id, result):
        client.disconnect()
        reactor.stop()
      

      def on_add_success(result):
        if not result:
          log.info("add torrent successful, was already enqueued")
          client.disconnect()
          reactor.stop()
        else:
          new_id = result
          c = client.core.set_torrent_move_completed_path(result, completed_dir)
          c.addCallback(lambda a: on_set_1(result, a))
          c.addErrback(on_add_fail)
          log.info("added new torrent: " + repr(result))
        new_id=None

      def on_add_fail(result):
        log.info("add torrent failed: " + repr(result) + str(result))
        client.disconnect()
        reactor.stop()

      def on_connect_success(result):
        log.info("connection successful: " + repr(result))
        c = client.core.add_torrent_magnet(fn, 
            {
              'download_location':download_dir,
              })

        c.addCallback(on_add_success)
        c.addErrback(on_add_fail)

      def on_connect_fail(result):
        log.info("connection fail: " + repr(result))
        reactor.stop()

      d.addCallback(on_connect_success)
      d.addErrback(on_connect_fail)
      return new_id
 
    res = _run_deluge(run, fn)
    print "result:", res

  def get_status(self, deluge_id):
    def _get_status(reactor, deluge_id):
      log.info('get status for ' + deluge_id)
    _run_deluge(_get_status, deluge_id)


if __name__ == "__main__":
  print "downloading"
  logging.basicConfig(level=logging.DEBUG)
  dl = DownloadProviderDeluge()
  dl.enqueue('magnet:?xt=urn:btih:MMOWXONNO7AKGQRGGNNW4KEP3FEWZTTR&dn=Boardwalk.Empire.S01E01.Boardwalk.Empire.HDTV.XviD-FQM&tr=http://tracker.openbittorrent.com/announce')
