# -*- coding: utf-8 -*-
#Modules xbmc
import xbmc, xbmcgui
import xbmcaddon

#python modules
import os, time, stat, re, copy, time
from xml.dom.minidom import parse, Document, _write_data, Node, Element
import htmlentitydefs
from html2text import *

# rdf modules
import feedparser
import urllib

# to decode html entities
from BeautifulSoup import BeautifulStoneSoup

__author__     = "Senufo"
__scriptid__   = "script.rss_atom"
__scriptname__ = "rss_atom"

__addon__      = xbmcaddon.Addon(id=__scriptid__)

__cwd__        = __addon__.getAddonInfo('path')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )


sys.path.append (__resource__)

url = 'http://linuxfr.org/news.atom'
url = 'http://www.lequipe.fr/Xml/actu_rss.xml'
headlines = []

#get actioncodes from keymap.xml/ keys.h
ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7
#ACTION_PARENT_DIR = 9
ACTION_MOVE_LEFT       =   1
ACTION_MOVE_RIGHT      =   2
ACTION_MOVE_UP         =   3
ACTION_MOVE_DOWN       =   4
ACTION_PAGE_UP         =   5
ACTION_PAGE_DOWN       =   6
ACTION_NUMBER1         =   59
ACTION_NUMBER2         =   60
ACTION_VOLUME_UP       =   88
ACTION_VOLUME_DOWN     =   89
ACTION_REWIND          =   78
ACTION_FASTFORWARD     =   77

#ID des boutons dans WinCourrier.xml
STATUS_LABEL   	= 100
NX_MAIL       	= 101
MSG_BODY	= 102
EMAIL_LIST     	= 120
SCROLL_BAR	= 121
MSG_BODY	= 102
SERVER1		= 1001
SERVER2		= 1002
SERVER3		= 1003
QUIT		= 1004
FILE_ATT	= 1005
#MAX_SIZE_MSG = int(Addon.getSetting( 'max_msg_size' ))
#SEARCH_PARAM = Addon.getSetting( 'search_param' )

class RSSWindow(xbmcgui.WindowXML):
   
  def __init__(self, *args, **kwargs):
    if xbmc:
        self.RssFeedsPath = xbmc.translatePath('special://userdata/RssFeeds.xml')
    else:
        self.RssFeedsPath = r'C:\Documents and Settings\Xerox\Application Data\XBMC\userdata\RssFeeds.xml'
    sane = True   #self.checkRssFeedPathSanity()
   
  def onInit( self ):
    print "Branch  EXPERIMENTAL"
    try:
        self.feedsTree = parse(self.RssFeedsPath)
    except:
        print "Erreur self.feedsTree"
    if self.feedsTree:
        #self.feedsList = self.getCurrentRssFeeds()
        self.feedsList = dict()
        sets = self.feedsTree.getElementsByTagName('set')
        for s in sets:
            setName = 'set'+s.attributes["id"].value
            self.feedsList[setName] = {'feedslist':list(), 'attrs':dict()}
            #get attrs
            for attrib in s.attributes.keys():
                self.feedsList[setName]['attrs'][attrib] = s.attributes[attrib].value
            #get feedslist
            feeds = s.getElementsByTagName('feed')
            for feed in feeds:
                self.feedsList[setName]['feedslist'].append({'url':feed.firstChild.toxml(), 'updateinterval':feed.attributes['updateinterval'].value})
        for setName in self.feedsList:
            val = setName[0]
            print "%s = %s " % (setName,val)
            print "url = %s " % self.feedsList[setName]
            #for set in feedsList[setName]:
            #    print "SET = %s" % set
            for feed in self.feedsList[setName]['feedslist']:
                    print "url = %s " % feed['url']
        print "URL = %s " % self.feedsList['set1']



    Dialog = xbmcgui.DialogProgress()
                              #Message(s)                       #Get mail
    Dialog.create("Connexion à : ", "LinuxFr")
    NbNews = 0
    Dialog.update(0, 'Connexion à', 'Please wait...')
    
    #Sauve les flux RSS
    for setName in self.feedsList:
        i = 0
        for feed in self.feedsList[setName]['feedslist']:
            i += 1
            print "=>url = %s " % feed['url']
            updateinterval = int(feed['updateinterval']) * 60
            #http://www.lequipe.fr/Xml/actu_rss.xml
            filename = feed['url']
            filename = re.sub('^http://.*/','Rss-',filename)
            self.RssFeeds = xbmc.translatePath('special://userdata/%s' % filename)
            date_modif = os.stat(self.RssFeeds).st_mtime
            diff = time.time() - date_modif
            #Si le flux date de plus que le updateinterval on le download de nx
            print "diff = %f, date_modif = %f, updateinterval %d" % (diff,date_modif,updateinterval )
            #if (diff > updateinterval):
            if True:
                print "=>filename = %s, self.RssFeeds = %s, url = %s " % (filename,self.RssFeeds, feed['url'])
                urllib.urlretrieve(feed['url'], filename = self.RssFeeds)
                print "date = %f, epoc time = %f  " % (date_modif, time.time())
            #Récupére le titre du FLUX
            print 'file://%s' % self.RssFeeds
            doc = feedparser.parse('file://%s' % self.RssFeeds)
            #print "doc Titre = %s " % doc.feed.title
            self.getControl( 1000 + i ).setLabel( doc.feed.title )
    # parse the document
    #doc = feedparser.parse(url)
    doc = feedparser.parse('file://%s' % self.RssFeeds)
    #Récupère le tire du flux
    #print "doc Titre = %s " % doc.feed.title
    img_name = ' '
    if doc.status < 400:
        for entry in doc['entries']:
            try:
                #unicode(s , enc).encode('utf8','replace')
                #print type(entry.title)
                title = unicode(entry.title)
                link  = unicode(entry.link)
                #title = (entry.title)
                #link  = (entry.link)
                if entry.has_key('enclosures'):
                    if entry.enclosures:
                        print "Enclosure = %s " % entry.enclosures[0].href
                        link_img = entry.enclosures[0].href
                        img_name = self.download(link_img,'/tmp/img.jpg')
                if entry.has_key('content') and len(entry['content']) >= 1:
                    description = unicode(entry['content'][0].value)
                    type = entry['content'][0].type
                    #print "Content = %s " % entry['content'][0].type
                else:
                    description = unicode(entry['summary_detail'].value)
                    type = 'text'
                headlines.append((title, link, description, type, img_name))
                NbNews += 1
                img_name = ' '
            except AttributeError, e:
                print "AttributeError : %s" % str(e)
                pass
    else:
        print ('Error %s, getting %r' % (doc.status, url))
    self.getControl( NX_MAIL ).setLabel( '%d news' % NbNews ) 
    Dialog.close()
    progressDialog = xbmcgui.DialogProgress()
                              #Message(s)                       #Get mail
    progressDialog.create("Connexion à : ", "LinuxFr")
    up = 1
    for titre,link,description,type,img_name in headlines:
        #print type(titre)
                   #Get mail                         Please wait
        try:    
            print "Headline = %s " % unicode(titre).encode('utf-8','replace')
            listitem = xbmcgui.ListItem( label=titre) 
            #listitem.setProperty( "realname", realname )
            #listitem.setProperty( "date", date )   
            html = html2text(description)
            listitem.setProperty( "message", html )
            listitem.setProperty( "img" , img_name )
            #listitem.setProperty( "att_file", att_file )
            self.getControl( 120 ).addItem( listitem )
            print "Up = %d,  NbNews = %d" % (up,NbNews)
            up2 = int((up*100)/NbNews)
            print "UP = %d " % up
            up += 1
            progressDialog.update(up2, 'Get News', 'Please wait...')



            #print "Description = %s " % unicode(html).encode('utf-8','replace')
        except Exception ,e:
            print "Erreur : %s " % str(e)
    progressDialog.close()       

  def getCacheThumbName(url, multiimagepath):
    thumb = xbmc.getCacheThumbName(url)
   
    if 'jpg' in url:
        thumb = thumb.replace('.tbn', '.jpg')
    elif 'png' in url:
        thumb = thumb.replace('.tbn', '.png')
    elif 'gif' in url:
        thumb = thumb.replace('.tbn', '.gif')
   
    tpath = os.path.join(multiimagepath, thumb)
    return tpath
     
  def checkDir(path):
    if not os.path.exists(path):
        os.mkdir(path)
 
  def download(self,src,dst):
    tmpname = xbmc.translatePath('special://temp/%s' % xbmc.getCacheThumbName(src))
    print "tmpname = %s " % tmpname 
    if os.path.exists(tmpname):
        os.remove(tmpname)
    urllib.urlretrieve(src, filename = tmpname)
    #os.rename(tmpname, dst)
    return tmpname

  def onAction(self, action):
        #print "ID Action %d" % action.getId()
        #print "Code Action %d" % action.getButtonCode()
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_MOVE_UP:
            controlId = action.getId()
        if action == ACTION_MOVE_DOWN:
            controlId = action.getButtonCode()
        if action == ACTION_FASTFORWARD: #PageUp
            if (self.position > 0):
                self.position = self.position - 1
            self.getControl( MSG_BODY ).scroll(self.position)
            print "Position F = %d " % self.position
        if (action == ACTION_REWIND): #PageUp
            #if (self.position <= self.nb_lignes):
            if (self.position <= 100):
                self.position = self.position + 1
            self.getControl( MSG_BODY ).scroll(self.position)
            print "Position R = %d " % self.position
																       
  def onClick( self, controlId ):
        #print "onClick controId = %d " % controlId
        if (controlId in [SERVER1,SERVER2,SERVER3]):
            label = self.getControl( controlId ).getLabel()
            self.checkEmail(label)
        elif (controlId == QUIT):
            self.close()




mydisplay = RSSWindow( "RSSWin.xml" , __cwd__, "Default")
mydisplay .doModal()
del mydisplay
