'''
    qobuz.node.favorite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''

from inode import INode
from qobuz.debug import warn
from qobuz.node import getNode, Flag
from qobuz.api import api
from qobuz.i8n import _

class Node_favorite(INode):
    '''Displaying user favorites (track and album)
    '''
    def __init__(self, parameters={}):
        super(Node_favorite, self).__init__(parameters)
        self.kind = Flag.FAVORITE
        self.label = _('Favorites')
        self.content_type = 'albums'
        self.items_path = self.get_parameter('items_path')
        if 'item_path' in self.parameters:
            del self.parameters['items_path']

    def get_label(self):
        return '%s / %s ' % (self.label, self.items_path)

    def url(self, **ka):
        if not 'items_path' in ka:
            ka['items_path'] = self.items_path
        return super(Node_favorite, self).url(**ka)

    def fetch(self, renderer=None):
        data = api.get('/favorite/getUserFavorites', 
                           user_id=api.user_id, 
                           limit=api.pagination_limit, 
                           offset=self.offset, type=self.items_path)
        if not data:
            warn(self, "Build-down: Cannot fetch favorites data")
            return False
        self.data = data
        return True

    def populate(self, renderer=None):
        return getattr(self, '_populate_%s' % (self.items_path))(renderer)

    def _populate_tracks(self, renderer):
        for track in self.data['tracks']['items']:
            node = getNode(Flag.TRACK, self.parameters)
            node.data = track
            self.append(node)
        return True

    def _populate_albums(self, renderer):
        for album in self.data['albums']['items']:
            node = getNode(Flag.ALBUM, self.parameters)
            node.data = album
            self.append(node)
        return True

    def _populate_artists(self, renderer):
        for artist in self.data['artists']['items']:
            node = getNode(Flag.ARTIST, self.parameters)
            node.data = artist
            self.append(node)
        return True

    def get_description(self):
        return self.get_property('description')

#    def gui_add_albums(self):
#        qnt, qid = int(self.get_parameter('qnt')), self.get_parameter('qid')
#        nodes = self.list_albums(qnt, qid)
#        if len(nodes) == 0:
#            notifyH(dialogHeading, lang(36004))
#            return False
#        ret = xbmcgui.Dialog().select(lang(36005), [
#           node.get_label() for node in nodes                              
#        ])
#        if ret == -1:
#            return False
#        album_ids = ','.join([node.nid for node in nodes])
#        if not self.add_albums(album_ids):
#            notifyH(dialogHeading, 'Cannot add album(s) to favorite')
#            return False
#        notifyH(dialogHeading, 'Album(s) added to favorite')
#        return True
#
#    def gui_add_artists(self):
#        qnt, qid = int(self.get_parameter('qnt')), self.get_parameter('qid')
#        nodes = self.list_artists(qnt, qid)
#        if len(nodes) == 0:
#            notifyH(dialogHeading, lang(36004))
#            return False
#        ret = xbmcgui.Dialog().select(lang(36007), [
#           node.get_label() for node in nodes                              
#        ])
#        if ret == -1:
#            return False
#        artist_ids = ','.join([str(node.nid) for node in nodes])
#        if not self.add_artists(artist_ids):
#            notifyH(dialogHeading, 'Cannot add artist(s) to favorite')
#            return False
#        notifyH(dialogHeading, 'Artist(s) added to favorite')
#        return True

#    def list_albums(self, qnt, qid):
#        album_ids = {}
#        nodes = []
#        if qnt & Flag.ALBUM == Flag.ALBUM:
#            node = getNode(Flag.ALBUM, {'nid': qid})
#            node.fetch(None, None, None, None)
#            album_ids[str(node.nid)] = 1
#            nodes.append(node)
#        elif qnt & Flag.TRACK == Flag.TRACK:
#            render = renderer(qnt, self.parameters)
#            render.depth = 1
#            render.whiteFlag = Flag.TRACK
#            render.blackFlag = Flag.NONE
#            render.asList = True
#            render.run()
#            if len(render.nodes) > 0:
#                node = getNode(Flag.ALBUM)
#                node.data = render.nodes[0].data['album']
#                album_ids[str(node.nid)] = 1
#                nodes.append(node)
#        else:
#            render = renderer(qnt, self.parameters)
#            render.depth = -1
#            render.whiteFlag = Flag.ALBUM
#            render.blackFlag = Flag.STOPBUILD & Flag.TRACK
#            render.asList = True
#            render.run()
#            for node in render.nodes:
#                if node.nt & Flag.ALBUM: 
#                    if not str(node.nid) in album_ids:
#                        album_ids[str(node.nid)] = 1
#                        nodes.append(node)
#                if node.nt & Flag.TRACK:
#                    render = renderer(qnt, self.parameters)
#                    render.depth = 1
#                    render.whiteFlag = Flag.TRACK
#                    render.blackFlag = Flag.NONE
#                    render.asList = True
#                    render.run()
#                    if len(render.nodes) > 0:
#                        newnode = getNode(Flag.ALBUM)
#                        newnode.data = render.nodes[0].data['album']
#                        if not str(newnode.nid) in album_ids:
#                            nodes.append(newnode)
#                            album_ids[str(newnode.nid)] = 1
#        return nodes

#    def add_albums(self, album_ids):
#        ret = api.favorite_create(album_ids=album_ids)
#        if not ret:
#            return False
#        self._delete_cache()
#        return True
#    
#    def add_artists(self, artist_ids):
#        ret = api.favorite_create(artist_ids=artist_ids)
#        if not ret:
#            return False
#        self._delete_cache()
#        return True
#

#
    def list_tracks(self, plugin, node):
        from node.renderer.list import ListRenderer
        track_ids = {}
        nodes = []
        if node.kind & Flag.TRACK == Flag.TRACK:
            node.fetch()
            track_ids[str(node.nid)] = 1
            nodes.append(node)
        else:
            render = ListRenderer()
            render.alive = False
            render.depth = -1
            render.whiteFlag = Flag.TRACK
            render.render(plugin, node)
            for node in iter(render):
                if not str(node.nid) in track_ids:
                    nodes.append(node)
                    track_ids[str(node.nid)] = 1
        return nodes
#
#    def list_artists(self, qnt, qid):
#        artist_ids = {}
#        nodes = []
#        if qnt & Flag.ARTIST == Flag.ARTIST:
#            node = getNode(Flag.ARTIST, {'nid': qid})
#            node.fetch(None, None, None, Flag.NONE)
#            artist_ids[str(node.nid)] = 1
#            nodes.append(node)
#        else:
#            render = renderer(qnt, self.parameters)
#            render.depth = -1
#            render.whiteFlag = Flag.ALBUM & Flag.TRACK
#            render.blackFlag = Flag.TRACK & Flag.STOPBUILD
#            render.asList = True
#            render.run()
#            for node in render.nodes:
#                artist = getNode(Flag.ARTIST, {'nid': node.get_artist_id()})
#                if not artist.fetch(None, None, None, Flag.NONE):
#                    continue
#                if not str(artist.nid) in artist_ids:
#                    nodes.append(artist)
#                    artist_ids[str(artist.nid)] = 1
#        return nodes
#
#    def add_tracks(self, track_ids):
#        ret = api.favorite_create(track_ids=track_ids)
#        if not ret:
#            return False
#        self._delete_cache()
#        return True
#
#    def _delete_cache(self):
#        limit = getSetting('pagination_limit')
#        key = cache.make_key('/favorite/getUserFavorites', 
#                           user_id=api.user_id, 
#                           limit=limit, 
#                           offset=self.offset)
#        return cache.delete(key)
#
#    def del_track(self, track_id):
#        if api.favorite_delete(track_ids=track_id):
#            self._delete_cache()
#            return True
#        return False
#
#    def del_album(self, album_id):
#        if api.favorite_delete(album_ids=album_id):
#            self._delete_cache()
#            return True
#        return False
#
#    def del_artist(self, artist_id):
#        if api.favorite_delete(artist_ids=artist_id):
#            self._delete_cache()
#            return True
#        return False
#
#    def gui_remove(self):
#        qnt, qid = int(self.get_parameter('qnt')), self.get_parameter('qid')
#        node = getNode(qnt, {'nid': qid})
#        ret = None
#        if qnt & Flag.TRACK == Flag.TRACK:
#            ret = self.del_track(node.nid)
#        elif qnt & Flag.ALBUM == Flag.ALBUM:
#            ret = self.del_album(node.nid)
#        elif qnt & Flag.ARTIST == Flag.ARTIST:
#            ret = self.del_artist(node.nid)
#        else:
#            raise Qerror(who=self, what='invalid_node_type', 
#                         additional=self.nt)
#        if not ret:
#            notifyH(dialogHeading, 
#                    'Cannot remove item: %s' % (node.get_label()))
#            return False
#        notifyH(dialogHeading, 
#                    'Item successfully removed: %s' % (node.get_label()))
#        url = self.make_url(nt=self.nt, nid='', nm='')
#        executeBuiltin(containerUpdate(url, True))
#        return True