# -*- coding: utf-8 -*-
#Modules xbmc
import xbmc, xbmcgui
import xbmcaddon

#python modules
import os, time, stat, re, copy, time
from xml.dom.minidom import parse, Document, _write_data, Node, Element
import pickle
import htmlentitydefs
import glob

# rdf modules
import feedparser
import urllib


__author__     = "Senufo"
__scriptid__   = "script.headlines"
__scriptname__ = "headlines"

__addon__      = xbmcaddon.Addon(id=__scriptid__)

__cwd__        = __addon__.getAddonInfo('path')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )


sys.path.append (__resource__)

#Variable pour stocker les news
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

#ID des boutons dans .xml
STATUS_LABEL   	= 100
NX_NEWS       	= 101
DESC_BODY	    = 102
FEEDS_LIST     	= 120
QUIT		    = 1004
VIDEO           = 1006
class RSSWindow(xbmcgui.WindowXML):
   
  def __init__(self, *args, **kwargs):
   self.RssFeedName = []
  
  def onInit( self ):
    print "Branch Master"
    #On lit le repertoire ou les flux ont ete sauve
    #et on recupere les titres des ces flux
    #Pour les mettre dans les boutons
    rss_path = __profile__
    files = glob.glob("%s/%s" % (rss_path,'*-pickle'))
    for f in files:
        pkl_file = open(f, 'rb')
        doc = pickle.load(pkl_file)
        pkl_file.close()
        listitem = xbmcgui.ListItem( label=doc.feed.title) 
        listitem.setProperty("serveur", f)
        #On rempli le control list du skin
        self.getControl( 1200 ).addItem( listitem )
    #On selectionne pour l'affichage le premier flux
    self.getControl( 1200 ).selectItem( 1 )
    label = self.getControl( 1200 ).getSelectedItem().getProperty('serveur')
    #On affiche le premier flux
    self.ParseRSS(label)

  #Nettoie le code HTML d'après rssclient de xbmc
  def htmlentitydecode(self,s):
    # code from http://snipplr.com/view.php?codeview&id=15261
    # First convert alpha entities (such as &eacute;)
    # (Inspired from http://mail.python.org/pipermail/python-list/2007-June/443813.html)
    def entity2char(m):
        entity = m.group(1)
        if entity in htmlentitydefs.name2codepoint:
            return unichr(htmlentitydefs.name2codepoint[entity])
        return u" "  # Unknown entity: We replace with a space.
    
    t = re.sub(u'&(%s);' % u'|'.join(htmlentitydefs.name2codepoint), entity2char, s)
  
    # Then convert numerical entities (such as &#233;)
    t = re.sub(u'&#(\d+);', lambda x: unichr(int(x.group(1))), t)
   
    # Then convert hexa entities (such as &#x00E9;)
    return re.sub(u'&#x(\w+);', lambda x: unichr(int(x.group(1),16)), t)

  def cleanText(self,txt):
    p = re.compile(r'\s+')
    txt = p.sub(' ', txt)
    
    txt = self.htmlentitydecode(txt)
    
    p = re.compile(r'<[^<]*?/?>')
    return p.sub('', txt)
  
  def ParseRSS(self,RssName):
    """
    Parse RSS or ATOM file with feedparser
    """
    print "RssName = %s " % RssName
    Dialog = xbmcgui.DialogProgress()
    Dialog.create("Get News")
    Dialog.update(0, 'Please wait... ')

    self.getControl( FEEDS_LIST ).reset()
    #Recupere l'adresse du flux dans self.RssFeedName
    #print "==>self.RssFeeds = %s" % (RssName)
    #Le nom du fichier sur lequel on a cliquer 
    #est dans RssName avec pickle ajoute à la fin
    self.RssFeeds = RssName.replace("-pickle",'')
    #Récupère le titre du flux
    img_name = ' '
    #Vide les headlines lors d'un nouveau appel
    headlines = []
    #On lit les news dans le fichier Rss-xxxx-headlines
    if (os.path.isfile('%s-headlines' % self.RssFeeds)):
        pkl_file = open(('%s-headlines' % self.RssFeeds), 'rb')
        headlines = pickle.load(pkl_file)
        pkl_file.close()
    else:
        print "Erreur ouverture HEADLINES"
    #On stocke le nb de news
    NbNews = len(headlines)
    #On affiche le nb de news dans le skin²
    self.getControl( NX_NEWS ).setLabel( '%d news' % NbNews )
    #Variable pour la progression dans la boite de dialogue²
    up = 1
    #On rempli le skin²
    for titre,date,description,type,img_name,link_video in headlines:
        try:    
            print "Headline = %s " % unicode(titre).encode('utf-8','replace')
            listitem = xbmcgui.ListItem( label=titre) 
            #html = html2text(description)
            #On nettoie le texte html pour l'affichage
            description = re.sub('(<[bB][rR][ /]>)|(<[/ ]*[pP]>)', '[CR]', description, re.DOTALL)
            html = self.cleanText(description)
            listitem.setProperty( "description", html )
            listitem.setProperty( "img" , img_name )
            listitem.setProperty( "date" , date )
            listitem.setProperty( "video" , link_video )
            self.getControl( FEEDS_LIST ).addItem( listitem )
            #print "Up = %d,  NbNews = %d" % (up,NbNews)
            up2 = int((up*100)/NbNews)
            #print "UP = %d " % up
            up += 1
            Dialog.update(up2, 'Get News', 'Please wait...')
        except Exception ,e:
            print "Erreur : %s " % str(e)
    Dialog.close()       

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
        Visible = self.getControl( FEEDS_LIST
                                ).getSelectedItem().getProperty('video')
        print "VISIBLE = %s " % Visible
        if 'False' in Visible:
            self.getControl( VIDEO ).setVisible( False )
        else:
            self.getControl( VIDEO ).setVisible( True )


        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_MOVE_UP:
            print "ACTION_MOVE_UP"
            controlId = action.getId()
            controlId = action.getButtonCode()
            print "controlId = %d " % controlId
            if (controlId == 1200):
                label = self.getControl( controlId
                                   ).getSelectedItem().getProperty('serveur')
                self.ParseRSS(label)

        if action == ACTION_MOVE_DOWN:
            print "ACTION_MOVE_DOWN"
            controlId = action.getButtonCode()
            print "controlId = %d " % controlId
            
            if (controlId == 1200):
                label = self.getControl( controlId
                                   ).getSelectedItem().getProperty('serveur')
                self.ParseRSS(label)

        if action == ACTION_FASTFORWARD: #PageUp
            if (self.position > 0):
                self.position = self.position - 1
            self.getControl( DESC_BODY ).scroll(self.position)
            print "Position F = %d " % self.position
        if (action == ACTION_REWIND): #PageUp
            if (self.position <= 100):
                self.position = self.position + 1
            self.getControl( DESC_BODY ).scroll(self.position)
            print "Position R = %d " % self.position
																       
  def onClick( self, controlId ):
        print "onClick controId = %d " % controlId
        if (controlId == 1200):
            label = self.getControl( controlId
                                   ).getSelectedItem().getProperty('serveur')
            self.ParseRSS(label)
        elif (controlId == VIDEO):
            label1 = self.getControl( controlId ).getLabel()
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            #label = win.getProperty('video')
            label = self.getControl( FEEDS_LIST
                                   ).getSelectedItem().getProperty('video')

            print "Label video = %s, Property = %s " % (label,label1)
            xbmc.executebuiltin("XBMC.PlayMedia(%s)" % ( label ) )

        elif (controlId == QUIT):
            self.close()

mydisplay = RSSWindow( "script-headlines-main.xml" , __cwd__, "Default")
mydisplay .doModal()
del mydisplay
