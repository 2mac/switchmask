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
__module_version__ = '3.0'
__module_description__ = 'Roleplaying character name switcher'
__module_author__ = 'David McMackins II'

import hexchat

BOLD = '\x02'
COLOR = '\x03'
GRAY_COLOR = '14'

color_messages = True
colors = {}
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
        mask = word_eol[1]

        if color_messages:
            colors[mask] = get_color(mask)

        masks[combo] = mask
        hexchat.prnt('Mask set to "{}" for channel {}'.format(mask, combo))
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

def format_payload(mask_color, text):
    color = mask_color
    payload = COLOR + color # reset color before building
    for c in text:
        if c == '"':
            if color == mask_color:
                color = GRAY_COLOR
                payload += COLOR + color
                payload += c
            else:
                payload += c
                color = mask_color
                payload += COLOR + color
        else:
            payload += c

    return payload + COLOR # reset color after building

def msg_hook(word, word_eol, userdata):
    combo = get_combo()
    payload = word_eol[0]

    try:
        mask = masks[combo]

        if color_messages:
            mask_color = get_color(mask)
            payload = format_payload(mask_color, payload)
            mask = COLOR + COLOR + '<' + BOLD + COLOR + mask_color + mask + COLOR + BOLD + '>'
        else:
            mask = '<' + mask + '>'

        msg = '{} {}'.format(mask, payload)
    except KeyError:
        msg = payload

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
