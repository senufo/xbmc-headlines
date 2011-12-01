# -*- coding: utf-8 -*-
#Modules xbmc
import xbmc, xbmcgui
import xbmcaddon

#python modules
import os, time, stat, re, copy
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

    #variable pour position dans le msg
    self.position = 0

  def onInit( self ):
    print "Branch  EXPERIMENTAL"
    progressDialog = xbmcgui.DialogProgress()
                              #Message(s)                       #Get mail
    progressDialog.create("Feed", "LinuxFr")
    up = 0

    # parse the document
    doc = feedparser.parse(url)
    if doc.status < 400:
        for entry in doc['entries']:
            try:
                #unicode(s , enc).encode('utf8','replace')
                #print type(entry.title)
                title = unicode(entry.title)
                link  = unicode(entry.link)
                #title = (entry.title)
                #link  = (entry.link)

                if entry.has_key('content') and len(entry['content']) >= 1:
                    description = unicode(entry['content'][0].value)
                    type = entry['content'][0].type
                    print "COntent = %s " % entry['content'][0].type
                else:
                    description = unicode(entry['summary_detail'].value)
                headlines.append((title, link, description, type))
                up += 1    #Get mail                         Please wait
                progressDialog.update(up, 'Get News', 'Please wait...')
            
            except AttributeError:
                pass
    else:
        print ('Error %s, getting %r' % (doc.status, url))
    self.getControl( NX_MAIL ).setLabel( '%d news' % up ) 
    for titre,link,description,type in headlines:
        #print type(titre)
        try:    
            print "Headline = %s " % unicode(titre).encode('utf-8','replace')
            listitem = xbmcgui.ListItem( label=titre) 
            #listitem.setProperty( "realname", realname )
            #listitem.setProperty( "date", date )   
            html = html2text(description)
            listitem.setProperty( "message", html )
            #listitem.setProperty( "att_file", att_file )
            self.getControl( 120 ).addItem( listitem )

            print "Description = %s " % unicode(html).encode('utf-8','replace')
        except Exception ,e:
            print "Erreur : %s " % str(e)
        progressDialog.close()       

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
