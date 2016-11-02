'''
    qobuz.gui.utils
    ~~~~~~~~~~~~~~~

    :part_of: xbmc-qobuz
    :copyright: (c) 2012-2016 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import os
import sys
import re

try:
    """Dirty trick that permit to import this module outside of xbmc
    All function using xbmc module will fail ...
    """
    import xbmc  # @UnresolvedImport
    import xbmcgui  # @UnresolvedImport
    import xbmcplugin  # @UnresolvedImport
    """Keyboard
    """
    class Keyboard(xbmc.Keyboard):

        def __init__(self, default, heading='', hidden=True):
            self.setHeading('Qobuz / %s' % heading)

except:
    print "QobuzXBMC WARNING: Used outside of xbmc, lot of thing broken"

import qobuz  # @UnresolvedImport
from qobuz.xbmcrpc import showNotification, getInfoLabels
from qobuz import config
from qobuz import debug
from qobuz.util import common as commonUtil

def getImage(name):
    if name is None:
        return ''
    if name.startswith('http'):
        return name
    if not config.path:
        return ''
    return os.path.join(config.path.image, name + '.png')


def notifyH(title, text, image=None, mstime=2000):
    """Notify for human... not using localized string :p
    """
    if image is None:
        image = getImage('icon-default-256')
    else:
        image = getImage(image)
    return showNotification(title=title, message=text, image=image,
                            displaytime=mstime)


def notify_log(title, text, **ka):
    return notifyH(title, text, image='icon-default-256', **ka)


def notify_error(title, text, **ka):
    return notifyH(title, text, image='icon-error-256', **ka)


def notify_warn(title, text, **ka):
    return notifyH(title, text, image='icon-warn-256', **ka)


def notify(title, text, image=None, mstime=2000):
    """Notification that wrap title and text parameter into lang()
    """
    if image is None:
        image = getImage('icon-default-256')
    else:
        image = getImage(image)
    return showNotification(title=lang(title),
                            message=lang(text),
                            image=image,
                            displaytime=mstime)


def dialogLoginFailure():
    """Dialog to be shown when we can't login into Qobuz
    """
    dialog = xbmcgui.Dialog()
    if dialog.yesno(lang(30010), lang(30036), lang(30042)):
        qobuz.addon.openSettings()
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False,
                                  updateListing=True, cacheToDisc=False)
    else:
        xbmc.executebuiltin('ActivateWindow(home)')
        return False


def dialogServiceTemporarilyUnavailable():
    """Dialog to be shown when Qobuz is not available (Maintenance)
    """
    dialog = xbmcgui.Dialog()
    dialog.ok('Qobuz Service Temporay Unavailable',
              'Qobuz service are down :/',
              'Check it later')
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=False,
                              updateListing=True, cacheToDisc=False)
    return False


def isFreeAccount():
    """Check if account if it's a Qobuz paid account
    """
    from qobuz.api.user import current
    return current.is_free_account()
    # from qobuz.api import api
    # data = api.get('/user/login', username=user.username,
    #                password=user.password)
    # if not data:
    #     return True
    # if not data['user']['credential']['id']:
    #     return True
    # return False


def dialogFreeAccount():
    """Show dialog when using free acccount
    """
    if qobuz.addon.getSetting('warn_free_account') != 'true':
        return
    dialog = xbmcgui.Dialog()
    ok = dialog.yesno(lang(30175), lang(30176), lang(30177), lang(30178))
    if ok:
        qobuz.addon.setSetting('warn_free_account', 'false')


def executeJSONRPC(json):
    return xbmc.executeJSONRPC(json)


def convert_color(color):
    if color.startswith('#'):
        return '%sFF' % color[1:]
    return color

def color(color, msg):
    return '[COLOR=%s]%s[/COLOR]' % (convert_color(color), msg)


def lang(langId):
    s = config.app.addon.getLocalizedString(langId)
    if not s:
        raise KeyError(langId)
    return s


def runPlugin(url):
    return 'XBMC.RunPlugin("%s")' % (url)


def containerUpdate(url, replace=False):
    if replace:
        replace = ', "replace"'
    else:
        replace = ''
    s = 'Container.Update("%s"%s)' % (url, replace)
    return s


def yesno(heading, line1, line2='', line3=''):
    dialog = xbmcgui.Dialog()
    return dialog.yesno(heading, line1, line2, line3)


def containerRefresh():
    return ('Container.Refresh')


def executeBuiltin(cmd):
    debug.warn('util', 'Executing builtin: {}', cmd)
    xbmc.executebuiltin("%s" % (cmd))


def containerViewMode():
    label = 'Container.Viewmode'
    data = getInfoLabels(labels=[label])
    if data:
        return data[label]
    return ''


def containerSortMethod():
    label = 'Container.SortMethod'
    data = getInfoLabels(labels=[label])
    if data:
        return data[label]
    return ''


def setResolvedUrl(**ka):
    return xbmcplugin.setResolvedUrl(**ka)
