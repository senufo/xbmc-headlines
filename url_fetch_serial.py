#!/usr/bin/env python
import urllib2
import time

#hosts = ["http://yahoo.com", "http://google.com", "http://amazon.com",
#"http://ibm.com", "http://apple.com"]
hosts = ["http://feeds.feedburner.com/xbmc",
        "http://www.lequipe.fr/Xml/actu_rss.xml",
        "http://freshmeat.net/index.atom",
        "http://lesgirondins.cestenfrance.net/feed/",
        "http://linuxfr.org/news.atom",
        "http://linuxfr.org/journaux.atom",
        "http://linuxfr.org/forums.atom",
        "http://www.lemonde.fr/rss/une.xml",
        "http://www.lemonde.fr/rss/videos.xml"]
 
start = time.time()
#grabs urls of hosts and prints first 1024 bytes of page
for host in hosts:
    url = urllib2.urlopen(host)
    print url.read(1024)

print "Elapsed Time: %s" % (time.time() - start)
