'''
    qobuz.service.monitor
    ~~~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import sys
from time import time
import xbmcaddon  # @UnresolvedImport
import xbmcgui  # @UnresolvedImport
import xbmc  # @UnresolvedImport

pluginId = 'plugin.audio.qobuz'
__addon__ = xbmcaddon.Addon(id=pluginId)
__addonversion__ = __addon__.getAddonInfo('version')
__addonid__ = __addon__.getAddonInfo('id')
__cwd__ = __addon__.getAddonInfo('path')
dbg = True
addonDir = __addon__.getAddonInfo('path')
libDir = xbmc.translatePath(os.path.join(addonDir, 'resources', 'lib'))
qobuzDir = xbmc.translatePath(os.path.join(libDir, 'qobuz'))
sys.path.append(libDir)
sys.path.append(qobuzDir)

from bootstrap import QobuzBootstrap
from debug import warn, log
from api import api
import threading
from cache import cache
from cache.cacheutil import clean_old
keyTrackId = 'QobuzPlayerTrackId'
keyMonitoredTrackId = 'QobuzPlayerMonitoredTrackId'


class MyPlayer(xbmc.Player):

    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        self.trackId = None
        self.lock = threading.Lock()

    def playlist(self):
        return xbmc.PlayList(0)

    def getProperty(self, key):
        """Wrapper to retrieve property from Xbmc Main Window
            Parameter:
                key: string, property that you want to get
            * Lock may be useless ...
        """
        try:
            if not self.lock.acquire(5):
                warn(self, "getProperty: Cannot acquire lock!")
                return ''
            return xbmcgui.Window(10000).getProperty(key)
        finally:
            self.lock.release()

    def setProperty(self, key, value):
        """Wrapper to set Xbmc Main window property
            Parameter:
                key: string, property name to set
                value: string, value to set
        """
        try:
            if not self.lock.acquire(5):
                warn(self, "setProperty: Cannot acquire lock!")
                return
            xbmcgui.Window(10000).setProperty(key, value)
        finally:
            self.lock.release()

    def onPlayBackEnded(self):
        nid = self.getProperty(keyTrackId)
        warn(self, "play back ended from monitor !!!!!!" + nid)
        return True

    def onPlayBackStopped(self):
        nid = self.getProperty(keyTrackId)
        warn(self, "play back stopped from monitor !!!!!!" + nid)
        return True

    def onPlayBackStarted(self):
        # workaroung bug, we are sometimes called multiple times.
        if self.trackId:
            if self.getProperty(keyTrackId) != self.trackId:
                self.trackId = None
            else:
                warn(self, "Already monitoring song id: %s" % (self.trackId))
                return False
        nid = self.getProperty(keyTrackId)
        if not nid:
            warn(self, "No track id set by the player...")
            return False
        self.trackId = nid
        elapsed = 0
        while elapsed <= 10:
            if not self.isPlayingAudio():
                self.trackId = None
                return False
            if self.getProperty(keyTrackId) != self.trackId:
                self.trackId = None
                return False
            elapsed += 1
            xbmc.sleep(1000)
        api.track_resportStreamingStart(nid)
        self.trackId = None
        return False


class Monitor(xbmc.Monitor):

    def __init__(self):
        super(Monitor, self).__init__()
        self.abortRequested = False
        self.garbage_refresh = 60
        self.last_garbage_on = time() - (self.garbage_refresh + 1)

    def onAbortRequested(self):
        self.abortRequested = True

    def onDatabaseUpdated(self, database):
        import sqlite3 as lite
        if database != 'music':
            return 0
        dbver = ""
        if xbmcaddon.Addon('xbmc.addon').getAddonInfo('version') == "12.0.0":
            dbver = "MyMusic32.db"
        else:
            dbver = "MyMusic37.db"
        dbfile = os.path.join(xbmc.translatePath('special://profile/'),
                              "Database", dbver)
        try:
            con = lite.connect(dbfile)
            cur = con.cursor()
            cur.execute('SELECT DISTINCT(IdAlbum), comment from song')
            data = cur.fetchall()
            for line in data:
                musicdb_idAlbum = line[0]
                import re
                try:
                    curl = re.search(u'curl=(.*)\)', line[1]).group(1)
                except:
                    continue
                sqlcmd = "SELECT rowid from art WHERE media_id=?"
                data2 = None
                try:
                    cur.execute(sqlcmd, str(musicdb_idAlbum))
                    data2 = cur.fetchone()
                except:
                    pass
                if data2 is None:
                    sqlcmd2 = str("INSERT INTO art VALUES ("
                                  "NULL, (?) , 'album', 'thumb', (?)"
                                  ")")
                    cur.execute(sqlcmd2, (str(musicdb_idAlbum), str(curl)))
                    con.commit()
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            return -1
        finally:
            if con:
                con.commit()
                con.close()
        return True

    def is_garbage_time(self):
        if time() > (self.last_garbage_on + self.garbage_refresh):
            return True
        return False

    def isIdle(self, since=1):
        try:
            if xbmc.getGlobalIdleTime() >= since:
                return True
            return False
        except:
            return False

    def cache_remove_old(self, **ka):
        self.last_garbage_on = time()
        clean_old(cache)

    def onSettingsChanged(self):
        pass

boot = QobuzBootstrap(__addon__, 0)
logLabel = 'QobuzMonitor'
import pprint
try:
    boot.bootstrap_app()
    monitor = Monitor()
    player = MyPlayer()
    alive = True
    while alive:
        alive = False
        try:
            alive = not monitor.abortRequested
        except Exception as e:
            print "Exception while getting abortRequested..."
            raise e
        if not alive:
            break
        if monitor.isIdle(60) and monitor.is_garbage_time():
            log(logLabel, 'Periodic cleaning...')
            monitor.cache_remove_old(limit=20)
        xbmc.sleep(1000)
    print '[%s] Exiting... bye!' % (logLabel)
except Exception as e:
    print '[%s] Exiting monitor' % (pluginId)
    print 'Exception: %s' % (pprint.pformat(e))
