'''
    qobuz.node.track
    ~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.constants import Mode
from qobuz.node import Flag, ErrorNoData
from qobuz.node.inode import INode
from qobuz import debug
from qobuz.gui.util import lang, getImage, runPlugin, getSetting
from qobuz.gui.contextmenu import contextMenu
from qobuz.api import api


class Node_track(INode):

    def __init__(self, parent=None, parameters={}, data=None):
        super(Node_track, self).__init__(parent=parent,
                                         parameters=parameters,
                                         data=data)
        self.nt = Flag.TRACK
        self.content_type = 'songs'
        self.qobuz_context_type = 'playlist'
        self.is_folder = False
        self.status = None
        self.image = getImage('song')
        self.purchased = False

    def fetch(self, Dir, lvl, whiteFlag, blackFlag):
        if blackFlag & Flag.STOPBUILD == Flag.STOPBUILD:
            return None
        return api.get('/track/get', track_id=self.nid)

    def populate(self, Dir, lvl, whiteFlag, blackFlag):
        return Dir.add_node(self)

    def make_local_url(self):
        scheme = 'http'
        return '{scheme}://{host}:{port}/qobuz/{album_id}/{nid}/file.mpc'.format(
                scheme=scheme,
                host=getSetting('httpd_host'),
                port=getSetting('httpd_port'),
                album_id=self.get_album_id(),
                nid=str(self.nid))

    def make_url(self, mode=Mode.PLAY, asLocalUrl=False, **ka):
        if asLocalUrl is True:
            return self.make_local_url()
        purchased = self.get_parameter('purchased')
        if purchased:
            ka['purchased'] = purchased
            self.purchased = True
        return super(Node_track, self).make_url(mode=mode,
                                                asLocalUrl=asLocalUrl,
                                                **ka)

    def get_label(self, fmt="%a - %t", default=None):
        fmt = fmt.replace("%a", self.get_artist())
        fmt = fmt.replace("%t", self.get_title())
        fmt = fmt.replace("%A", self.get_album())
        fmt = fmt.replace("%n", str(self.get_track_number()))
        fmt = fmt.replace("%g", self.get_genre())
        return fmt

    def get_composer(self):
        return self.get_property('composer/name', default=-1)

    def get_interpreter(self):
        return self.get_property('performer/name', default=-1)

    def get_album(self):
        album = self.get_property('album/title', default=None)
        if album is not None:
            return album
        if self.parent and (self.parent.nt & Flag.ALBUM):
            return self.parent.get_title()
        return u''

    def get_album_id(self):
        aid = self.get_property('album/id')
        if not aid and self.parent:
            return self.parent.nid
        return aid

    def get_image(self):
        image = self.get_property(['album/image/large', 'image/large',
                                   'image/small',
                                   'image/thumbnail', 'image'], default=None)

        if image is not None:
            return image
        if self.parent and self.parent.nt & (Flag.ALBUM | Flag.PLAYLIST):
            return self.parent.get_image()
        return u''

    def get_playlist_track_id(self):
        return self.get_property('playlist_track_id')

    def get_position(self):
        return self.get_property('position')

    def get_title(self):
        return self.get_property('title')

    def get_genre(self):
        genre = self.get_property('album/genre/name', default=None)
        if genre is not None:
            return genre
        if self.parent is not None:
            return self.parent.get_genre()
        return u''

    def get_streaming_url(self):
        data = self.__getFileUrl()
        if not data:
            return None
        if 'url' not in data:
            debug.warn(self, "streaming_url, no url returned\n"
                 "API Error: %s" % (api.error))
            return None
        return data['url']

    def get_artist(self, by='track'):
        if by == 'album':
            artist = self.get_property(['album/artist/name',
                                        'performer/name'], default=None)
            if artist is None:
                if self.parent:
                    artist = self.parent.get_artist()
            if artist is None:
                return u''
            return artist
        return self.get_property(['artist/name',
                                  'composer/name',
                                  'performer/name',
                                  'interpreter/name',
                                  'composer/name',
                                  'album/artist/name'])

    def get_artist_id(self):
        return self.get_property(['artist/id',
                               'composer/id',
                               'performer/id',
                               'interpreter/id'], default=None, to='int')

    def get_track_number(self):
        return self.get_property('track_number', default=0, to='int')

    def get_media_number(self):
        return self.get_property('media_number', default=0, to='int')

    def get_duration(self):
        return self.get_property('duration')

    def get_year(self):
        import time
        date = self.get_property('album/released_at', default=None)
        if date is None:
            if self.parent is not None and self.parent.nt & Flag.ALBUM:
                return self.parent.get_year()
        year = 0
        try:
            year = time.strftime("%Y", time.localtime(date))
        except Exception as e:
            debug.warn(self, 'Invalid date format %s', date)
        return year

    def is_playable(self):
        url = self.get_streaming_url()
        if not url:
            return False
        restrictions = self.get_restrictions()
        if 'TrackUnavailable' in restrictions:
            return False
        if 'AlbumUnavailable' in restrictions:
            return False
        return True

    def get_hires(self):
        return self.get_property('hires')

    def get_purchased(self):
        return self.get_property('purchased')

    def get_description(self):
        if self.parent:
            return self.parent.get_description()
        return ''

    def __getFileUrl(self):
        hires = getSetting('hires_enabled', asBool=True)
        format_id = 6 if getSetting('streamtype') == 'flac' else 5
        if hires and self.get_hires():
            format_id = 27
        if self.get_property('purchased') or self.get_parameter('purchased') == '1' or self.purchased:
            intent = "download"
        else:
            intent = "stream"
        data = api.get('/track/getFileUrl', format_id=format_id,
                       track_id=self.nid, user_id=api.user_id, intent=intent)
        if not data:
            debug.warn(self, "Cannot get stream type for track (network problem?)")
            return None
        return data

    def get_restrictions(self):
        data = self.__getFileUrl()
        if not data:
            raise ErrorNoData('Cannot get track restrictions')
        restrictions = []
        if not 'restrictions' in data:
            return restrictions
        for restriction in data['restrictions']:
            restrictions.append(restriction['code'])
        return restrictions

    def is_sample(self):
        data = self.__getFileUrl()
        if not data:
            return False
        if 'sample' in data:
            return data['sample']
        return False

    def get_mimetype(self):
        data = self.__getFileUrl()
        if not data:
            return False
        if not 'format_id' in data:
            debug.warn(self, "Cannot get mime/type for track (restricted track?)")
            return False
        formatId = int(data['format_id'])
        mime = ''
        if formatId in [6, 27]:
            mime = 'audio/flac'
        elif formatId == 5:
            mime = 'audio/mpeg'
        else:
            debug.warn(self, "Unknow format " + str(formatId))
            mime = 'audio/mpeg'
        return mime

    def item_add_playing_property(self, item):
        """ We add this information only when playing item because it require
        us to fetch data from Qobuz
        """
        mime = self.get_mimetype()
        if not mime:
            debug.warn(self, "Cannot set item streaming url")
            return False
        item.setProperty('mimetype', mime)
        item.setPath(self.get_streaming_url())
        return True

    def makeListItem(self, replaceItems=False):
        import xbmcgui  # @UnresolvedImport
        current_mode = self.get_parameter('mode', to='int')
        media_number = self.get_media_number()
        if not media_number:
            media_number = 1
        else:
            media_number = int(media_number)
        duration = self.get_duration()
        if duration is None:
            debug.error(self, "no duration\n%s" % (pprint.pformat(self.data)))
        label = self.get_label(fmt='%a - %t')
        if current_mode == Mode.SCAN:
            label = self.get_label(fmt='%t')
        isplayable = 'true'
        # Disable free account checking here, purchased track are
        # still playable even with free account, but we don't know yet.
        # if qobuz.gui.is_free_account():
        #    duration = 60
        # label = '[COLOR=FF555555]' + label + '[/COLOR]
        # [[COLOR=55FF0000]Sample[/COLOR]]'
        image = self.get_image()
        url = self.make_url(mode=Mode.PLAY)
        item = xbmcgui.ListItem(label, self.get_label(), image, image, url)
        if not item:
            debug.warn(self, "Cannot create xbmc list item")
            return None
        item.setIconImage(image)
        item.setThumbnailImage(image)
        item.setPath(url)
        track_number = self.get_track_number()
        if not track_number:
            track_number = 0
        else:
            track_number = int(track_number)
        mlabel = self.get_property('label/name')
        '''Xbmc Library fix: Compilation showing one entry by track
            We are setting artist like 'VA / Artist'
            Data snippet:
                {u'id': 26887, u'name': u'Interpr\xe8tes Divers'}
                {u'id': 145383, u'name': u'Various Artists'}
                {u'id': 255948, u'name': u'Multi Interpretes'}
        '''
        # artist = self.get_artist()
        # if self.parent and hasattr(self.parent, 'get_artist_id'):
        #     if self.parent.get_artist() != artist:
        #         artist = '%s / %s' % (self.parent.get_artist(), artist)
        #description or 'Qobuz Music Streaming'
        comment = u'''
Popularity: {popularity}
copyright: {copyright}
description: {description}
'''.format(popularity=self.get_property('popularity', default='n/a'),
            copyright=self.get_property('copyright', default=''),
            description=self.get_description())

        item.setInfo(type='Music', infoLabels={
                     'count': self.nid,
                     'title': label,
                     'album': self.get_album(),
                     'genre': self.get_genre(),
                     'artist': self.get_artist(),
                     'album_artist': self.get_artist(by='album'),
                     'tracknumber': track_number,
                     'duration': duration,
                     'year': self.get_year(),
                     'comment': comment,
                     'rating': self.get_property('album/popularity'),
        })
        item.setProperty('DiscNumber', str(media_number))
        item.setProperty('IsPlayable', isplayable)
        item.setProperty('IsInternetStream', isplayable)
        item.setProperty('Music', isplayable)
        ctxMenu = contextMenu()
        self.attach_context_menu(item, ctxMenu)
        item.addContextMenuItems(ctxMenu.getTuples(), replaceItems)
        return item

    def attach_context_menu(self, item, menu):
        if self.parent and (self.parent.nt & Flag.PLAYLIST == Flag.PLAYLIST):
            colorCaution = getSetting('item_caution_color')
            url = self.parent.make_url(nt=Flag.PLAYLIST,
                                       id=self.parent.nid,
                                       qid=self.get_playlist_track_id(),
                                       nm='gui_remove_track',
                                       mode=Mode.VIEW)
            menu.add(path='playlist/remove',
                     label=lang(30075),
                     cmd=runPlugin(url), color=colorCaution)

        ''' Calling base class '''
        super(Node_track, self).attach_context_menu(item, menu)
