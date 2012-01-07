#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.

import sys
import urllib
import xbmcplugin, xbmcgui, xbmc

from constants import *

class QobuzGUI:

  def __init__( self, bootstrap):
      self.Bootstrap = bootstrap

  
  '''
      Must be called at the end for folder to be displayed
  '''
  def endOfDirectory(self):
      return xbmcplugin.endOfDirectory(int(sys.argv[1]))
  
  '''
  Top-level menu
  '''
  def showCategories(self):
     i = self.Bootstrap.Images
     __language__ = self.Bootstrap.__language__
     xbmcplugin.setPluginFanart(int(sys.argv[1]), i.get('fanart'))
     self._add_dir(__language__(30013), '', MODE_SEARCH_SONGS, i.get('song'), 0)
     self._add_dir(__language__(30014), '', MODE_SEARCH_ALBUMS, i.get('album'), 0)
     self._add_dir(__language__(30015), '', MODE_SEARCH_ARTISTS, i.get('album'), 0)
     self._add_dir(__language__(30082), '', MODE_SHOW_RECOS, i.get('song'), 0)
     if (self.Bootstrap.Core.Api.userid != 0):
        self._add_dir(__language__(30019), '', MODE_USERPLAYLISTS, i.get('playlist'), 0)
     print "Sbo"
  
  """
      Search for songs
  """
  def searchSongs(self):
     __language__ = self.Bootstrap.__language__
     query = self._get_keyboard(default="",heading=__language__(30020))
     if (query != ''):
       s = self.Bootstrap.Core.getQobuzSearchTracks()
       s.search(query, 100)#self.Bootstrap.__addon__.getSetting('songsearchlimit'))
       if s.length() > 0:
           s.add_to_directory()
       else:
           xbmc.executebuiltin('XBMC.Notification(' + __language__(30008) + ',' + __language__(30021)+ ', 2000, ' + self.Bootstrap.Images.get('default') + ')')
           self.searchSongs()
     else:
        self.showCategories()
  
  """
      Search for Albums
  """
  def searchAlbums(self):
     __language__ = self.Bootstrap.__language__
     query = self._get_keyboard(default="",heading=__language__(30020))
     if (query != ''):
       s = self.Bootstrap.Core.getQobuzSearchAlbums()
       s.search(query, self.Bootstrap.__addon__.getSetting('albumsearchlimit'))
       if s.length() > 0:
           s.add_to_directory()
       else:
           xbmc.executebuiltin('XBMC.Notification(' + __language__(30008) + ',' + __language__(30021)+ ', 2000, ' + thumbDef + ')')
           self.searchAlbums()
     else:
        self.showCategories()

  """
      Search for Artists
  """
  def searchArtists(self):
     __language__ = self.Bootstrap.__language__
     query = self._get_keyboard(default="",heading=__language__(30020))
     if (query != ''):
       s = self.Bootstrap.Core.getQobuzSearchArtists()
       s.search(query, self.Bootstrap.__addon__.getSetting('artistsearchlimit'))
       if s.length() > 0:
           s.add_to_directory()
       else:
           xbmc.executebuiltin('XBMC.Notification(' + __language__(30008) + ',' + __language__(30021)+ ', 2000, ' + thumbDef + ')')
           self.searchAlbums()
     else:
        self.categories()

  """
      Show Recommendations 
  """
  def showRecommendations(self, type, genre_id):
     if (genre_id != ''):
       r = self.Bootstrap.Core.getRecommandation(genre_id, type)
       r.fetch_data()
       if r.length() > 0:
         r.add_to_directory()
       else:
          dialog = xbmcgui.Dialog()
          dialog.ok(__language__(30008),__language__(30021))
          self.showRecommendationsGenres(type)

  def showRecommendationsTypes(self):
     __language__ = self.Bootstrap.__language__
     i = self.Bootstrap.Images
     xbmcplugin.setPluginFanart(int(sys.argv[1]), i.get('fanart'))
     self._add_dir(__language__(30083), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=press-awards','', i.get('song'), 0)
     self._add_dir(__language__(30084), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=new-releases','', i.get('song'), 0)
     self._add_dir(__language__(30085), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=best-sellers','', i.get('song'), 0)
     self._add_dir(__language__(30086), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T)+'&type=editor-picks','', i.get('song'), 0)

  def showRecommendationsGenres(self, type):
     __language__ = self.Bootstrap.__language__
     i = self.Bootstrap.Images
     self._add_dir(__language__(30087), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=112',MODE_SHOW_RECO_T_G, i.get('song'), 0)
     self._add_dir(__language__(30088), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=64',MODE_SHOW_RECO_T_G, i.get('song'), 0)
     self._add_dir(__language__(30089), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=80',MODE_SHOW_RECO_T_G, i.get('song'), 0)
     self._add_dir(__language__(30090), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=6',MODE_SHOW_RECO_T_G, i.get('song'), 0)
     self._add_dir(__language__(30091), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=64',MODE_SHOW_RECO_T_G, i.get('song'), 0)
     self._add_dir(__language__(30092), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=94',MODE_SHOW_RECO_T_G, i.get('song'), 0)
     self._add_dir(__language__(30093), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=2',MODE_SHOW_RECO_T_G, i.get('song'), 0)
     self._add_dir(__language__(30094), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=91',MODE_SHOW_RECO_T_G, i.get('song'), 0)
     self._add_dir(__language__(30095), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=10',MODE_SHOW_RECO_T_G, i.get('song'), 0)
     self._add_dir(__language__(30096), sys.argv[0]+'?mode='+str(MODE_SHOW_RECO_T_G)+'&type='+type+'&genre=null',MODE_SHOW_RECO_T_G, i.get('song'), 0)


#
  # Get my playlists
  def showUserPlaylists(self):
    user_playlists = self.Bootstrap.Core.getUserPlaylists()
    user_playlists.add_to_directory()
    try: pass
    except:
      dialog = xbmcgui.Dialog()
      dialog.ok(__language__(30008), __language__(30033))
      self.showCategories()

      # Get album
  def showProduct (self, id):
    album = self.Bootstrap.Core.getProduct(id)
    album.add_to_directory()
    try: pass
    except:
      dialog = xbmcgui.Dialog()
      dialog.ok(__language__(30008), __language__(30033))

  def showArtist (self, id):
    album = self.Bootstrap.Core.getProductsFromArtist()
    album.get_by_artist(id)
    album.add_to_directory_by_artist()
    try: pass
    except:
      dialog = xbmcgui.Dialog()
      dialog.ok(__language__(30008), __language__(30033))


  # Show selected playlist
  def showPlaylist(self, id):
     userid = self.Bootstrap.Core.Api.userid
     if (userid != 0):
        myplaylist = self.Bootstrap.Core.getPlaylist(id)
        myplaylist.add_to_directory()
     else:
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30008), __language__(30034), __language__(30040))

  # Get keyboard input
  def _get_keyboard(self, default="", heading="", hidden=False):
     kb = xbmc.Keyboard(default, heading, hidden)
     kb.doModal()
     if (kb.isConfirmed()):
        return unicode(kb.getText(), "utf-8")
     return ''

  # Add whatever directory
  def _add_dir(self, name, url, mode, iconimage, id, items=1):

     if url == '':
        u=sys.argv[0]+"?mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&id="+str(id)
     else:
        u = url
     dir=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
     dir.setInfo( type="Music", infoLabels={ "title": name } )

     # Custom menu items
     menuItems = []
     if mode == MODE_ALBUM:
        mkplaylst=sys.argv[0]+"?mode="+str(MODE_MAKE_PLAYLIST)+"&name="+name+"&id="+str(id)
        menuItems.append((__language__(30076), "XBMC.RunPlugin("+mkplaylst+")"))
     if mode == MODE_PLAYLIST:
        rmplaylst=sys.argv[0]+"?mode="+str(MODE_REMOVE_PLAYLIST)+"&name="+urllib.quote_plus(name)+"&id="+str(id)
        menuItems.append((__language__(30077), "XBMC.RunPlugin("+rmplaylst+")"))
        mvplaylst=sys.argv[0]+"?mode="+str(MODE_RENAME_PLAYLIST)+"&name="+urllib.quote_plus(name)+"&id="+str(id)
        menuItems.append((__language__(30078), "XBMC.RunPlugin("+mvplaylst+")"))

     dir.addContextMenuItems(menuItems, replaceItems=False)

     return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=dir,isFolder=True, totalItems=items)