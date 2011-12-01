# -*- coding: utf-8 -*-

#python modules
import os, time, stat, re, copy
import htmlentitydefs

# rdf modules
import feedparser
import urllib

# to decode html entities
from BeautifulSoup import BeautifulStoneSoup

url = 'http://linuxfr.org/news.atom'
headlines = []

def htmlenties2txt(string):
    """
    Converts a string to a string with all html entities resolved.
    Returns the result as Unicode object (that may conatin chars outside 256.
    """
    e = copy.deepcopy(htmlentitydefs.entitydefs)
    e['ndash'] = "-";
    e['bull'] = "-";
    e['rsquo'] = "'";
    e['lsquo'] = "`";
    e['hellip'] = '...'

    string = unicode(string).replace("&#039", "'").replace("&#146;", "'")

    i = 0
    while i < len(string):
        amp = string.find("&", i) # find & as start of entity
        if amp == -1: # not found
            break
        i = amp + 1

        semicolon = string.find(";", amp) # find ; as end of entity
        if string[amp + 1] == "#": # numerical entity like "&#039;"
            entity = string[amp:semicolon+1]
            try:
                replacement = unicode(unichr(int(entity[2:-1])))
            except UnicodeError:
                replacement = unichr(int(entity[2:-1]))
        else:
            entity = string[amp:semicolon + 1]
            if semicolon - amp > 7:
                continue
            try:
                # the array has mappings like "Uuml" -> "ü"
                replacement = e[entity[1:-1]]
            except KeyError:
                continue
        try:
            string = string.replace(entity, replacement.decode("latin-1"))
        except UnicodeError:
            string = string.replace(entity, replacement)
    return string

# parse the document
doc = feedparser.parse(url)
if doc.status < 400:
    for entry in doc['entries']:
        try:
            #unicode(s , enc).encode('utf8','replace')
            print type(entry.title)
            title = unicode(entry.title)
            link  = unicode(entry.link)
            #title = (entry.title)
            #link  = (entry.link)

            if entry.has_key('content') and len(entry['content']) >= 1:
                description = unicode(entry['content'][0].value)
            else:
                description = unicode(entry['summary_detail'].value)
            headlines.append((title, link, description))
        except AttributeError:
            pass
else:
    print ('Error %s, getting %r' % (doc.status, url))

for titre,link,description in headlines:
    print type(titre)
    try:    
        print "Headline = %s " % unicode(titre).encode('utf-8','replace')
        description = description.replace('\n\n', '&#xxx;').replace('\n', ' ').\
                          replace('&#xxx;', '\n')
        description = description.replace('<p>', '\n').replace('<br>', '\n')
        description = description.replace('<p>', '\n').replace('<br/>', '\n')
        description = description + '\n \n \nLink: ' + link
        description = unicode(BeautifulStoneSoup(description, convertEntities=BeautifulStoneSoup.HTML_ENTITIES))
        description = htmlenties2txt(description)

        print "Description = %s " % unicode(description).encode('utf-8','replace')
    except Exception ,e:
        print "Erreur : %s " % str(e)
       

