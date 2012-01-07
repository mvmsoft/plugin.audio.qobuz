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
from constants import *

class IQobuzTag(object):
    
    def __init__(self, json = None):
        self.__valid_tags = None
        self.__is_loaded = None
        self.__json = json
        
    def parse_json(self, json):
        assert("load_json must be overloaded")
    
    def set_valid_tags(self, tags):
        self.__valid_tags = tags
    
    def get(self, key):
        if not self.is_loaded():
            assert("Json is not loaded")
        if key not in self.__valid_tags:
            assert("Invalid tag: " + key)
        return self.__dict__[key]
    
    def set(self, key, value):
        if key not in self.__valid_tags:
            assert("Invalid tag:" + key)
        v = ''
        try:
            v = str(value)
        except:
            if isinstance(value, basestring):
                v = value.encode('utf8', 'ignore')
            elif isinstance(value, bool):
                if value: v = '1'
                else: v = '0'
        #print "setting " + key + ": " + v + "\n"
        self.__dict__[key] = v
    
    def is_loaded(self):
        return self.__is_loaded
    
    def getTitle(self):
        v = 'N/A'
        try:
            v = self.title
        except: pass
        return v
    
    def getArtist(self):
        label = []
        try:
            label.append(self.artist)
        except:
            try:
                label.append(self.interpreter_name)
            except: 
                try:
                    label.append(self.composer_name)
                except: label.append('N/A')
        return ''.join(label)
    
    def getGenre(self):
        genre = ''
        try:
            genre = self.genre
        except:
            genre = 'N/A'
        return genre
    
    def getDuration(self):
        (sh,sm,ss) = self.duration.split(':')
        return (int(sh) * 3600 + int(sm) * 60 + int(ss))
    
    def getYear(self):
        date = ''
        try:
            date = self.release_date
        except:
            try:
                date = self.released_at
                #print "Date: " + date
            except:
                try:
                    date = self.created_at
                except: pass
        if not date:
            return date
        year = 0
        try: 
            year = int(date.split('-')[0])
        except: pass
        return year
    
    def getImage(self):
        image = ''
        try:
            image = self.image_large
        except:
            try:
                image = self.image_small
            except:
                try:
                    image = self.image_thumbnail
                except: pass
        return image
'''
'''
class QobuzTagUserPlaylist(IQobuzTag):
    
    def __init__(self, json):
        super(QobuzTagUserPlaylist, self).__init__(json)
        self.set_valid_tags(['id', 'name', 'description', 'position', 
                             'created_at', 'updated_at', 'is_public', 
                             'is_collaborative', 'owner_id', 'owner_name', 'length'])
        if json:
            self.parse_json(json)
    
    def parse_json(self, p):
        #print "Parsing...\n"
        self.set('id', p['id'])
        self.set('name', p['name'])
        self.set('description', p['description'])
        try:
            self.set('position', p['position'])
        except: pass
        try:
            self.set('created_at', p['created_at'])
        except: pass
        try:
            self.set('updated_at', p['updated_at'])
        except: pass
        self.set('is_public', p['is_public'])
        self.set('is_collaborative', p['is_collaborative'])
        self.set('owner_id', p['owner']['id'])
        self.set('owner_name', p['owner']['name'])
        try:
            p['length']
            self.set('length', p['length'])
        except:
            self.set('length', '-1')
        self._is_loaded = True

class QobuzTagArtist(IQobuzTag):
    
    def __init__(self, json):
        super(QobuzTagArtist, self).__init__(json)
        self.set_valid_tags(['id', 'name'])
        self.__album = None
        if json:
            self.parse_json(json)

        
    def getArtist(self):
        return self.name
    
    def get_album(self):
        return self.__album
    
    def parse_json(self, p):
        self.set('id', p['id'])
        self.set('name', p['artist']['name'])
        self.__album = QobuzTagAlbum(p)
        self._is_loaded = True
        
'''
'''
class QobuzTagAlbum(IQobuzTag):
    
    def __init__(self, json):
        super(QobuzTagAlbum, self).__init__(json)
        self.set_valid_tags(['id', 'title', 'genre', 'label', 'image_large', 
                             'release_date'])
        if json:
            self.parse_json(json)
    
    def parse_json(self, p):
        self.set('id', p['id'])
        self.set('title', p['title'])
        try:
            self.set('label', p['label'])
        except: pass
        try:
            self.set('genre', p['genre']['name'])
        except: pass
        try:
            self.set('image_large', p['image']['large'])
        except: pass
        try:
            self.set('release_date', p['release_date'])
        except:
            try:
                self.set('released_at', p['released_at'])
            except: pass
        try:
            self.set('subtitle', p['subtitle'])
        except: pass
        self._is_loaded = True

'''
'''
class QobuzTagProduct(IQobuzTag):
    
    def __init__(self, json):
        super(QobuzTagProduct, self).__init__(json)
        self.set_valid_tags(['id', 'artist_name', 'genre', 'description',
                            'image_large', 'image_small', 'image_thumbnail', 
                            'label', 'price', 'realease_date', 'relevancy', 
                            'title', 'type', 'url'])
        if json:
            self.parse_json(json)
    
    def parse_json(self, p):
        self.set('id', p['id'])
        self.set('artist', p['artist'])
        self.set('genre', p['genre'])
        self.set('image_large', p['image']['large'])
        self.set('image_large', p['image']['small'])
        self.set('image_small', p['image']['thumbnail'])
        self.set('label', p['label'])
        self.set('price', p['price'])
        self.set('release_date', p['release_date'])
        self.set('relevancy', p['relevancy'])
        self.set('title', p['title'])
        self.set('type', p['type'])
        self.set('url', p['url'])
        self._is_loaded = True

'''
'''
class QobuzTagTrack(IQobuzTag):
    
    def __init__(self, json):
        super(QobuzTagTrack, self).__init__(json)
        self.set_valid_tags(['playlist_track_id', 'position', 'id', 'title', 
                             'interpreter_name', 'interpreter_id', 
                             'composer_name', 'composer_id',
                             'tracke_numer', 'media_number', 'duration',
                             'created_at', 'streaming_type'])
        self.__album = None
        if json:
            self.parse_json(json)
        
    def get_album(self):
        return self.__album
    
    def getLabel(self):
        label = []
        label.append(self.track_number)
        label.append(' - ')
        label.append(self.getArtist())
        label.append(' - ')
        label.append(self.title)
        return ''.join(label)
    
    def parse_json(self, p):
        self.set('id', p['id'])
        try:
            self.set('playlist_track_id', p['playlist_track_id'])
        except: pass
        self.set('title', p['title'])
        try:
            self.set('interpreter_name', p['interpreter']['name'])
            self.set('interpreter_id', p['interpreter']['id'])
        except: pass
        try:
            self.set('composer_id', p['composer_id'])
            self.set('composer_name', p['composer_name'])
        except: pass
        try:
            self.set('position', p['position'])
        except: pass
        self.set('track_number', p['track_number'])
        self.set('media_number', p['media_number'])
        self.set('duration', p['duration'])
        try:
            self.set('created_at', p['created_at'])
        except: pass
        self.set('streaming_type', p['streaming_type'])
        self.__album = QobuzTagAlbum(p['album'])
        self._is_loaded = True

'''
'''
class QobuzTagPlaylist(IQobuzTag):
    
    def __init__(self, json):
        super(QobuzTagPlaylist, self).__init__(json)
        self.set_valid_tags([])
        self.__user_playlist = None
        self.__tracks__ = []
        if json:
            self.parse_json(json)
            
    def get_user_playlist(self):
        return self.__user_playlist
    
    def get_tracks(self):
        return self.__tracks__
    
    def parse_json(self, p):
        self.__user_playlist = QobuzTagUserPlaylist(p)
        for track in p['tracks']:
            self.__tracks__.append(QobuzTagTrack(track))
        self._is_loaded = True
        
