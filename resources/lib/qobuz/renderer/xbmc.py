'''
    qobuz.renderer.xbmc
    ~~~~~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import sys
import qobuz  # @UnresolvedImport
from qobuz import debug
from qobuz.renderer.irenderer import IRenderer
from qobuz.gui.util import notifyH, getSetting, setSetting
from qobuz import exception
from qobuz import config
from qobuz.node.flag import Flag
from qobuz.constants import Mode
from qobuz.node import getNode
from qobuz.gui.directory import Directory
from qobuz.alarm import Notifier

notifier = Notifier(title='Scanning progress')

class QobuzXbmcRenderer(IRenderer):
    """Specific renderer for Xbmc
        Parameter:
            node_type: int, node type (node.NodeFlag)
            params: dictionary, parameters passed to our plugin
        * You can set parameter after init (see renderer.Irenderer)
    """

    def __init__(self, node_type, params={}, mode=None, whiteFlag=Flag.ALL,
                 blackFlag=Flag.STOPBUILD):
        super(QobuzXbmcRenderer, self).__init__(node_type, params, mode,
                                                whiteFlag=whiteFlag,
                                                blackFlag=blackFlag)

    def run(self):
        '''Building our tree, creating root node based on our node_type
        '''
        if not self.set_root_node():
            debug.warn(self, ("Cannot set root node ({}, {})") %
                (str(self.node_type), str(self.root.get_parameter('nid'))))
            return False
        if self.root.hasWidget:
            return self.root.displayWidget()
        if self.has_method_parameter():
            return self.execute_method_parameter()
        from qobuz.gui.directory import Directory
        Dir = Directory(self.root, self.nodes, handle=config.app.handle,
                        withProgress=self.enable_progress, asList=self.asList)
        if getSetting('contextmenu_replaceitems', asBool=True):
            Dir.replaceItems = True
        try:
            ret = self.root.populating(Dir,
                                       self.depth,
                                       self.whiteFlag,
                                       self.blackFlag)
        except exception.QobuzError as e:
            Dir.end_of_directory(False)
            Dir = None
            debug.warn(self,
                       "Error while populating our directory: %s" % (repr(e)))
            return False
        if not self.asList:
            import xbmcplugin  # @UnresolvedImport
            Dir.set_content(self.root.content_type)
            methods = [
                xbmcplugin.SORT_METHOD_UNSORTED,
                xbmcplugin.SORT_METHOD_LABEL,
                xbmcplugin.SORT_METHOD_DATE,
                xbmcplugin.SORT_METHOD_TITLE,
                xbmcplugin.SORT_METHOD_VIDEO_YEAR,
                xbmcplugin.SORT_METHOD_GENRE,
                xbmcplugin.SORT_METHOD_ARTIST,
                xbmcplugin.SORT_METHOD_ALBUM,
                xbmcplugin.SORT_METHOD_PLAYLIST_ORDER,
                xbmcplugin.SORT_METHOD_TRACKNUM, ]
            [xbmcplugin.addSortMethod(handle=config.app.handle,
                                      sortMethod=method) for method in methods]
        return Dir.end_of_directory()

    def scan(self):
        '''Building tree when using Xbmc library scanning
        feature
        '''
        if not self.set_root_node():
            debug.warn(self, "Cannot set root node ('{}')",
                       str(self.node_type))
            return False
        Dir = Directory(self.root, nodes=self.nodes, withProgress=False,
                        handle=config.app.handle, asLocalUrl=True)
        notifier.notify('Scanning root directory: %s' % self.root.label,
                        check=True)
        tracks = {}
        #self.root.set_parameter('mode', Mode.SCAN)
        # if self.root.nt & Flag.TRACK == Flag.TRACK:
        #
        #     self.root.fetch()
        #     tracks[self.root.nid] = self.root
        #
        # else:
        def list_track(root):
            predir = Directory(None, asList=True)
            findir = Directory(None, asList=True)
            if root.nt & Flag.TRACK == Flag.TRACK:
                predir.add_node(root)
            else:
                root.populating(predir, -1, Flag.ALL, Flag.STOPBUILD)
            seen = {}
            seen_tracks = {}
            for node in predir.nodes:
                node.set_parameter('mode', Mode.SCAN)
                notifier.notify(node.get_label(), check=True)
                notifier.check()
                if node.nt & Flag.TRACK == Flag.TRACK:
                    if node.nid in seen_tracks:
                        continue
                    seen_tracks[node.nid] = 1
                    album_id = node.get_album_id()
                    if album_id is None or album_id == '':
                        debug.error(self,
                                    'Track without album_id: {}, label: {}',
                                    node, node.get_label().encode('ascii', errors='ignore'))
                        #findir.add_node(node)
                        continue
                    seen[album_id] = 1
                    album = getNode(Flag.ALBUM,
                                    parameters={
                                        'nid': album_id,
                                        'mode': Mode.SCAN
                                    })
                    album.populating(findir, -1, Flag.TRACK, Flag.STOPBUILD)
                else:
                    node.populating(findir, -1, Flag.TRACK, Flag.STOPBUILD)
            return findir.nodes

        tracks.update({track.nid: track for track in list_track(self.root)})
        if len(tracks.keys()) == 0:
            return False
        import xbmcgui
        ret = xbmcgui.Dialog().select('Add to library?', [
            node.get_label('%a - %t (%A)') for nid, node in tracks.items()
        ])
        if ret == -1:
            return False
        for nid, track in tracks.items():
            Dir.add_node(track)
        Dir.set_content(self.root.content_type)
        Dir.end_of_directory()
        notifyH('Scanning results',
                '%s items where scanned' % str(Dir.total_put),
                mstime=3000)
        return True
