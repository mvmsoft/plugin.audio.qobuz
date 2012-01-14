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
import os
import random
import xbmcgui
import xbmcplugin

import pprint

from debug import log, info, warn
from constants import *
from utils.icacheable import ICacheable
from utils.tag import QobuzTagArtist
from utils.tag import QobuzTagProduct
from data.genre_image import QobuzGenreImage

"""
    Class QobuzGetRecommendation
"""
class QobuzGetRecommandation(ICacheable):

    def __init__(self, Core, genre_id, type ='new-releases', limit = 100):
        self.Core = Core
        self.genre_id = genre_id
        self.type = type
        self.limit = limit 
        super(QobuzGetRecommandation, self).__init__(self.Core.Bootstrap.cacheDir,
                                                     'recommandations-' + type,
                                                     genre_id)
        self.set_cache_refresh(self.Core.Bootstrap.__addon__.getSetting('cache_duration_recommandation'))
        info(self, "Cache duration: " + str(self.cache_refresh))
        self.fetch_data()
      
    def _fetch_data(self):
        return self.Core.Api.get_recommandations(self.genre_id, 
                                                self.type, self.limit)
    def length(self):
        return len(self.get_raw_data())
    
    def set_image_genre(self, image):
        info(self, "Set image genre to: " + image)
        cache = QobuzGenreImage(self.Core)
        cache.set(self.type, self.genre_id, image)
        
    def add_to_directory(self):
        n = self.length()
        h = int(sys.argv[1])
        rand = random.randint(0, n)
        print "rand: " + str(rand)
        i = 0
        for json_product in self.get_raw_data():
            album = QobuzTagProduct(json_product)
            if i == rand:
                image = album.getImage()
                if image:
                    print "Image: " + image
                    self.set_image_genre(image)
            u = self.Core.Bootstrap.build_url(MODE_ALBUM, album.id)
            item = album.getXbmcItem()

            xbmcplugin.addDirectoryItem(handle=h, url=u, listitem=item, 
                                        isFolder=True, totalItems=n)
            i += 1
        xbmcplugin.addSortMethod(h,xbmcplugin.SORT_METHOD_LABEL)
        return n
