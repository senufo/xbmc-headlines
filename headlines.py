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

class RSSWindow(xbmcgui.WindowXML):
   
  def __init__(self, *args, **kwargs):
    #On efface toutes les anciennes images des flux
    Img_path = xbmc.translatePath('special://temp/')
    files = glob.glob("%s/%s" % (Img_path,'*.tbn'))
    for f in files:
            os.remove(f)
    self.position = 0
#Recupere le chemoin de RssFeeds.xml
    self.RssFeedName = []
    if xbmc:
        #Crée le répertoire user_data/script.rss_atom si il n'existe pas
        if not (os.path.isdir(__profile__)):
            os.mkdir(__profile__)
        self.RssFeedsPath = xbmc.translatePath('special://userdata/RssFeeds.xml')
    else:
        #A vérifier sous windows, non testé !!
        self.RssFeedsPath = r'C:\Documents and Settings\Xerox\Application Data\XBMC\userdata\RssFeeds.xml'
   
  def onInit( self ):
    print "Branch Master"
    try:
        self.feedsTree = parse(self.RssFeedsPath)
    except:
        print "Erreur self.feedsTree"
    #Recupere la liste des flux dans RSSFeeds.xml
    if self.feedsTree:
        self.feedsList = dict()
        sets = self.feedsTree.getElementsByTagName('set')
        #print "SET = %s " % sets
        for s in sets:
            setName = 'set'+s.attributes["id"].value
            print "SETNAME = %s " % setName
            self.feedsList[setName] = {'feedslist':list(), 'attrs':dict()}
            #get attrs
            for attrib in s.attributes.keys():
                self.feedsList[setName]['attrs'][attrib] = s.attributes[attrib].value
            #get feedslist
            feeds = s.getElementsByTagName('feed')
            for feed in feeds:
                self.feedsList[setName]['feedslist'].append({'url':feed.firstChild.toxml(), 'updateinterval':feed.attributes['updateinterval'].value})
        #for setName in self.feedsList:
        #    val = setName[0]
        #    print "%s = %s " % (setName,val)
        #    print "url = %s " % self.feedsList[setName]
            #for set in feedsList[setName]:
            #    print "SET = %s" % set
        #    for feed in self.feedsList[setName]['feedslist']:
        #            print "url = %s " % feed['url']
        #print "URL = %s " % self.feedsList['set1']



    Dialog = xbmcgui.DialogProgress()
                              #Message(s)                       #Get mail
    Dialog.create("Connexion  ", " ")
    NbNews = 0
    time_debut = time.time()
    print "TIME debut = %f " % time.time() 
    #Sauve les flux RSS
    for setName in self.feedsList:
        i = 0
        for feed in self.feedsList[setName]['feedslist']:
            i += 1
            #print "=>url = %s " % feed['url']
            Dialog.update(0, 'Connexion : %s' % feed['url'], 'Please wait...')
            updateinterval = int(feed['updateinterval']) * 60
            filename = feed['url']
            filename = re.sub('^http://.*/','Rss-',filename)
            self.RssFeeds = '%s/%s' % (__profile__,filename)
            #teste si le fichier existe
            #if (os.path.isfile(self.RssFeeds)):
                #Si le flux est plus ancien que le updateinterval on le telecharge de nouveau
            #    date_modif = os.stat(self.RssFeeds).st_mtime
            #    diff = time.time() - date_modif
                #print "diff = %f, date_modif = %f, updateinterval %d" % (diff,date_modif,updateinterval )

                #Si le flux est plus ancien que le updateinterval on le telecharge de nouveau
            #    if (diff > updateinterval):
            #        #print "=>filename = %s, self.RssFeeds = %s, url = %s " % (filename,self.RssFeeds, feed['url'])
            #        urllib.urlretrieve(feed['url'], filename = self.RssFeeds)
                    #On efface le fichier parser²
            #        os.remove('%s-pickle' % self.RssFeeds)
            #        #print "date = %f, epoc time = %f  " % (date_modif, time.time())
            #else:
                #Le fichier n'existe pas on le download
            #    urllib.urlretrieve(feed['url'], filename = self.RssFeeds)
            #Récupére le titre du FLUX
            print 'file://%s' % self.RssFeeds
            #Si il existe deja parser on lit le fichier
            if (os.path.isfile('%s-pickle' % self.RssFeeds)):
                pkl_file = open(('%s-pickle' % self.RssFeeds), 'rb')
                doc = pickle.load(pkl_file)
                pkl_file.close()
            else:
                #Sinon on parse le fichier rss et on le sauve sur le disque
                doc = feedparser.parse('file://%s' % self.RssFeeds)
                #Sauve le doc parse directement
                output = open(('%s-pickle' % self.RssFeeds), 'wb')
                # Pickle dictionary using protocol 0.
                pickle.dump(doc, output)
                output.close()
            #print "doc Titre = %s " % doc.feed.title
            #self.getControl( 1000 + i ).setLabel( doc.feed.title )
            #On rempli la liste des serveurs + le titre du flux
            self.RssFeedName.append((self.RssFeeds,doc.feed.title))
            listitem = xbmcgui.ListItem( label=doc.feed.title) 
            #listitem.setProperty( "att_file", att_file )
            listitem.setProperty("serveur", self.RssFeeds)
            #On rempli le control list du skin²
            self.getControl( 1200 ).addItem( listitem )
            time_int = time.time() - time_debut
            print "time int = %f " % time_int

    time_int = time.time() - time_debut
    print "TIME FIN = %f " % time_int
    print "rssfeed = %s " % self.RssFeeds
    #On affiche les dernier flux
    self.ParseRSS(self.RssFeeds)

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
    #est dans RssName
    self.RssFeeds = RssName
    NbNews = 0
    # parse the document
    #Si c'est deja fait on lit le fichier 
    if (os.path.isfile('%s-pickle' % self.RssFeeds)):
        pkl_file = open(('%s-pickle' % self.RssFeeds), 'rb')
        doc = pickle.load(pkl_file)
        pkl_file.close()
    else:
        #Sinon on le parse
        doc = feedparser.parse('file://%s' % self.RssFeeds)
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
    #On recupere les tags suivants :
    #title, entry.content, enclosure pour les images
    #et date
    #if doc.status < 400:
    #    for entry in doc['entries']:
    #        try:
    #            title = unicode(entry.title)
    #            #link  = unicode(entry.link)
    #            #Recupere un media associe
    #            if entry.has_key('enclosures'):
    #                if entry.enclosures:
    #                    print "Enclosure = %s " % entry.enclosures[0].href
    #                    print "Enclosure = %s " % entry.enclosures[0].type
    #                    #actuellement que les images
    #                    if 'image' in entry.enclosures[0].type:
    #                        link_img = entry.enclosures[0].href
    #                        img_name = self.download(link_img,'/tmp/img.jpg')
    #            #C'est ici que le recupere la news²
    #            if entry.has_key('content') and len(entry['content']) >= 1:
    #                description = unicode(entry['content'][0].value)
    #                #type contient le type de texte : html, plain text, etc...
    #                type = entry['content'][0].type
    #            else:
    #                #Si pas de content on essaye le summary_detail
    #                description = unicode(entry['summary_detail'].value)
    #                type = 'text'
    #            #Recuperation de la date de la news
    #            if entry.has_key('date'):
    #                date = entry['date']
    #            else:
    #                date = 'unknown'
    #            #On rempli les news
    #            headlines.append((title, date, description, type, img_name))
    #            NbNews += 1
    #            #On vide le nom de l'image pour le prochain tour
    #            img_name = ' '
    #        except AttributeError, e:
    #            print "AttributeError : %s" % str(e)
    #            pass
    #else:
    #    print ('Error %s, getting %r' % (doc.status, url))
    #On sauve le headlines dans un fichier
    #output = open(('%s-headlines' % self.RssFeeds), 'wb')
    # Pickle dictionary using protocol 0.
    #pickle.dump(headlines, output)
    #output.close()

    #On affiche le nb de news dans le skin²
    self.getControl( NX_NEWS ).setLabel( '%d news' % NbNews )
    #Variable pour la progression dans la boite de dialogue²
    up = 1
    #On rempli le skin²
    for titre,date,description,type,img_name in headlines:
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
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_MOVE_UP:
            controlId = action.getId()
        if action == ACTION_MOVE_DOWN:
            controlId = action.getButtonCode()
        if action == ACTION_FASTFORWARD: #PageUp
            if (self.position > 0):
                self.position = self.position - 1
            self.getControl( DESC_BODY ).scroll(self.position)
            print "Position F = %d " % self.position
        if (action == ACTION_REWIND): #PageUp
            #if (self.position <= self.nb_lignes):
            if (self.position <= 100):
                self.position = self.position + 1
            self.getControl( DESC_BODY ).scroll(self.position)
            print "Position R = %d " % self.position
																       
  def onClick( self, controlId ):
        print "onClick controId = %d " % controlId
        if (controlId == 1200):
            #label = self.getControl( controlId ).getSelectedItem().getLabel()
            label = self.getControl( controlId
                                   ).getSelectedItem().getProperty('serveur')
            #print "LABEL LIST = %s" % (repr(label))
            self.ParseRSS(label)
        elif (controlId == QUIT):
            self.close()




mydisplay = RSSWindow( "script-headlines-main.xml" , __cwd__, "Default")
mydisplay .doModal()
del mydisplay
