#!/usr/bin/env python
import Queue
import threading
import urllib2
import time

#hosts = ["http://yahoo.com", "http://google.com", "http://amazon.com",
#        "http://ibm.com", "http://apple.com"]
hosts = ["http://feeds.feedburner.com/xbmc",
        "http://www.lequipe.fr/Xml/actu_rss.xml",
        "http://freshmeat.net/index.atom",
        "http://lesgirondins.cestenfrance.net/feed/",
        "http://linuxfr.org/news.atom",
        "http://linuxfr.org/journaux.atom",
        "http://linuxfr.org/forums.atom",
        "http://www.lemonde.fr/rss/une.xml",
        "http://www.lemonde.fr/rss/videos.xml"]
 
queue = Queue.Queue()

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            #grabs host from queue
            host = self.queue.get()

            #grabs urls of hosts and prints first 1024 bytes of page
            url = urllib2.urlopen(host)
            print url.read(1024)

            #signals to queue job is done
            self.queue.task_done()

start = time.time()
def main():
    
    #spawn a pool of threads, and pass them queue instance 
    for i in range(5):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()

    #populate queue with data
    for host in hosts:
        queue.put(host)
    
    #wait on the queue until everything has been processed
    queue.join()
main()
print "Elapsed Time: %s" % (time.time() - start)
