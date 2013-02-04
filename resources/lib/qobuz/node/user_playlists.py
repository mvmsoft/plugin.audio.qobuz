'''
    qobuz.node.user_playlists
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
from qobuz.node import Flag, getNode
from inode import INode
from qobuz.debug import warn
from qobuz.api import api
from xbmcpy.util import lang

class Node_user_playlists(INode):
    """User playlists node
        This node list playlist made by user and saved on Qobuz server
    """
    def __init__(self, parameters = {}):
        super(Node_user_playlists, self).__init__(parameters)
        self.kind = Flag.USERPLAYLISTS
        self.label = lang(30000)
        self.content_type = 'files'
        self.offset = self.get_parameter('offset')

    def fetch(self, renderer=None):
        data = api.get('/playlist/getUserPlaylists', 
                       limit=api.pagination_limit, offset=self.offset, 
                       user_id=api.user_id)
        if not data:
            warn(self, "Build-down: Cannot fetch user playlists data")
            return False
        self.data = data
        return True

    def populate(self, renderer=None):
        for playlist in self.data['playlists']['items']:
            node = getNode(Flag.PLAYLIST, self.parameters)
            node.data = playlist
            self.append(node)
        return True
