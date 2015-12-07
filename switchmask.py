##
##  SwitchMask - Manage your identity.
##  Copyright (C) 2015 David McMackins II
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License as published by
##  the Free Software Foundation, version 3 only.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU Affero General Public License for more details.
##
##  You should have received a copy of the GNU Affero General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

__module_name__ = 'SwitchMask'
__module_version__ = '2.1'
__module_description__ = 'Roleplaying character name switcher'
__module_author__ = 'David McMackins II'

import hexchat

_COLOR_CODE = '\x03'

masks = {}

def get_combo():
    network = hexchat.get_info('network')
    channel = hexchat.get_info('channel')
    return '{}:{}'.format(network, channel)

def get_color(text):
    color = 2

    for c in text:
        color += ord(c)
        while color > 13:
            color -= 12

    code = format(color, '02d')
    return code

def add_mask(word, word_eol, userdata):
    combo = get_combo()

    try:
        text = word_eol[1]
        color = get_color(text)
        mask = color + text

        masks[combo] = mask
        hexchat.prnt('Mask set to "{}" for channel {}'.format(text, combo))
    except IndexError:
        try:
            hexchat.prnt('Mask for channel {} is "{}"'.format(combo,
                                                              masks[combo]))
        except KeyError:
            hexchat.prnt('No mask set for channel {}'.format(combo))

    return hexchat.EAT_ALL

def remove_mask(word, word_eol, userdata):
    combo = get_combo()

    try:
        del masks[combo]
        hexchat.prnt('Removed mask for {}'.format(combo))
    except KeyError:
        pass

    return hexchat.EAT_ALL

def send(msg):
    hexchat.command('MSG {} {}'.format(hexchat.get_info('channel'), msg))

def msg_hook(word, word_eol, userdata):
    combo = get_combo()

    try:
        msg = '<\x02\x03{}\x03\x02> {}'.format(masks[combo], word_eol[0])
    except KeyError:
        msg = word_eol[0]

    send(msg)
    return hexchat.EAT_ALL

def unmasked_message(word, word_eol, userdata):
    send(word_eol[1])
    return hexchat.EAT_ALL

def unload(userdata):
    hexchat.prnt('{} unloaded'.format(__module_name__))

def init():
    hexchat.hook_command('mask', add_mask)
    hexchat.hook_command('unmask', remove_mask)
    hexchat.hook_command('unmasked', unmasked_message)
    hexchat.hook_command('', msg_hook)
    hexchat.hook_unload(unload)
    hexchat.prnt('Loaded {} {}'.format(__module_name__, __module_version__))

init()
