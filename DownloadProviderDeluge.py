import logging
from DownloadProvider import DownloadProvider
from multiprocessing import Process, Queue

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

    def run(reactor, fn):
      log.info("should download " + str(fn))
      d = client.connect()
      reactor.resi = 5

      def on_add_success(result):
        if not result:
          log.info("add torrent successful, was already enqueued")
        else:
          log.info("added new torrent: " + repr(result))
        reactor.resi = result
        client.disconnect()
        reactor.stop()

      def on_add_fail(result):
        log.info("add torrent failed: " + repr(result))
        client.disconnect()
        reactor.stop()

      def on_connect_success(result):
        log.info("connection successful: " + repr(result))
        home = '/home/mru/06multimedia/serial_rent/'
        c = client.core.add_torrent_magnet(fn, 
            {
              'download_location':home+'torrents',
              #'move_on_completed': true,
              #'move_on_completed_path': home+'torrents_done'
              })

        c.addCallback(on_add_success)
        c.addErrback(on_add_fail)

      def on_connect_fail(result):
        log.info("connection fail: " + repr(result))
        reactor.stop()

      d.addCallback(on_connect_success)
      d.addErrback(on_connect_fail)
      return reactor.resi
 
    res = _run_deluge(run, fn)
    print "result:", res

  def get_status(self, deluge_id):
    def _get_status(reactor, deluge_id):
      log.info('get status for ' + deluge_id)
    _run_deluge(_get_status, deluge_id)


