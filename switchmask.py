##
## SwitchMask - Manage your identity.
## Copyright (C) 2015-2017 David McMackins II
##
## Redistributions, modified or unmodified, in whole or in part, must retain
## applicable copyright or other legal privilege notices, these conditions, and
## the following license terms and disclaimer.  Subject to these conditions,
## the holder(s) of copyright or other legal privileges, author(s) or
## assembler(s), and contributors of this work hereby grant to any person who
## obtains a copy of this work in any form:
##
## 1. Permission to reproduce, modify, distribute, publish, sell, sublicense,
## use, and/or otherwise deal in the licensed material without restriction.
##
## 2. A perpetual, worldwide, non-exclusive, royalty-free, irrevocable patent
## license to reproduce, modify, distribute, publish, sell, use, and/or
## otherwise deal in the licensed material without restriction, for any and all
## patents:
##
##     a. Held by each such holder of copyright or other legal privilege,
##     author or assembler, or contributor, necessarily infringed by the
##     contributions alone or by combination with the work, of that privilege
##     holder, author or assembler, or contributor.
##
##     b. Necessarily infringed by the work at the time that holder of
##     copyright or other privilege, author or assembler, or contributor made
##     any contribution to the work.
##
## NO WARRANTY OF ANY KIND IS IMPLIED BY, OR SHOULD BE INFERRED FROM, THIS
## LICENSE OR THE ACT OF DISTRIBUTION UNDER THE TERMS OF THIS LICENSE,
## INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR
## A PARTICULAR PURPOSE, AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS,
## ASSEMBLERS, OR HOLDERS OF COPYRIGHT OR OTHER LEGAL PRIVILEGE BE LIABLE FOR
## ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN ACTION OF CONTRACT, TORT,
## OR OTHERWISE ARISING FROM, OUT OF, OR IN CONNECTION WITH THE WORK OR THE USE
## OF OR OTHER DEALINGS IN THE WORK.
##

__module_name__ = 'SwitchMask'
__module_version__ = '3.3.1'
__module_description__ = 'Roleplaying character name switcher'
__module_author__ = 'David McMackins II'

import hexchat

from os.path import exists
from pickle import dump, load

BOLD = '\x02'
ITALIC = '\x1D'
COLOR = '\x03'
GRAY_COLOR = '14'

COLOR_NAMES = (
    'white',
    'black',
    'navy',
    'green',
    'red',
    'maroon',
    'purple',
    'orange',
    'yellow',
    'lightgreen',
    'teal',
    'cyan',
    'blue',
    'magenta',
    'gray',
    'lightgray'
)

class TextProperties:
    def __init__(self):
        self.color = ''
        self.bold = False
        self.italic = False

    def __str__(self):
        s = ''

        if self.color:
            s += COLOR + self.color

        if self.bold:
            s += BOLD

        if self.italic:
            s += ITALIC

        return s

    def __len__(self):
        return len(str(self))

class UserPrefs:
    def __init__(self):
        self.color_messages = True
        self.color_overrides = {}
        self.masks = {}
        self.colors = {}

PREFS = UserPrefs()

STATE_FILE_PATH = '{}/switchmask.state'.format(hexchat.get_info('configdir'))
try:
    if exists(STATE_FILE_PATH):
        with open(STATE_FILE_PATH, 'rb') as f:
            PREFS = load(f)
except Exception as e:
    hexchat.prnt(str(e))

def color_name_lookup(name):
    return format(COLOR_NAMES.index(name), '02d')

COLOR_DEMO = ''
for name in COLOR_NAMES:
    COLOR_DEMO += COLOR + color_name_lookup(name) + name + ' '
COLOR_DEMO = COLOR_DEMO.rstrip()

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

    if len(word_eol) < 2:
        if combo in PREFS.masks:
            hexchat.prnt('Mask for {} is "{}"'.format(combo,
                                                      PREFS.masks[combo]))
        else:
            hexchat.prnt('No mask set for {}'.format(combo))

        return hexchat.EAT_ALL

    mask = word_eol[1]

    PREFS.masks[combo] = mask
    PREFS.colors[combo] = get_color(mask)
    hexchat.prnt('Mask set to "{}" for {}'.format(mask, combo))

    return hexchat.EAT_ALL

def remove_mask(word, word_eol, userdata):
    combo = get_combo()

    if combo in PREFS.masks:
        del PREFS.masks[combo]
        hexchat.prnt('Removed mask for {}'.format(combo))

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

def get_msg_len():
    n = 512 # IRC RFC 2812
    n -= 3 # hexchat does this
    n -= 13 # command length
    nick = hexchat.get_info('nick')
    n -= len(nick)
    n -= len(hexchat.get_info('channel'))

    users = hexchat.get_list('users')
    for user in users:
        if user.nick == nick:
            if user.host:
                n -= len(user.host)
            else:
                n -= 9
                n -= 65

            break

    return n

def recolor_msg(msg):
    properties = TextProperties()
    parts = msg.split(' ')
    size = 0
    msg_len = get_msg_len()
    out = ''
    for part in parts:
        new_part = part
        if size + len(part) + len(properties) >= msg_len:
            new_part = str(properties) + part
            size = 0

        if COLOR in part:
            i = len(part) - part[::-1].index(COLOR) - 1
            properties.color = part[i+1:i+3]

        for _ in range(part.count(BOLD)):
            properties.bold = not properties.bold

        for _ in range(part.count(ITALIC)):
            properties.italic = not properties.italic

        out += new_part + ' '
        size += len(new_part) + 1

    return out.rstrip()

def msg_hook(word, word_eol, userdata):
    combo = get_combo()
    payload = word_eol[0]

    if combo not in PREFS.masks:
        return hexchat.EAT_NONE

    mask = PREFS.masks[combo]

    if PREFS.color_messages:
        if combo in PREFS.color_overrides:
            mask_color = PREFS.color_overrides[combo]
        else:
            mask_color = PREFS.colors[combo]

        payload = format_payload(mask_color, payload)
        mask = COLOR + COLOR + '<' + BOLD + COLOR + mask_color + mask + COLOR + BOLD + '>'
    else:
        mask = '<' + mask + '>'

    msg = '{} {}'.format(mask, payload)

    if PREFS.color_messages:
        msg = recolor_msg(msg)

    send(msg)
    return hexchat.EAT_ALL

def override_mask_color(word, word_eol, userdata):
    if len(word_eol) != 2:
        hexchat.prnt('USAGE: /' + word[0] + ' <color>')
        hexchat.prnt('Colors: ' + COLOR_DEMO)
        return hexchat.EAT_ALL

    color_name = word_eol[1].strip()

    if color_name in COLOR_NAMES:
        color = color_name_lookup(color_name)
        combo = get_combo()
        PREFS.color_overrides[combo] = color
        hexchat.prnt('Color for ' + combo + ' set to ' + COLOR + color
                     + color_name + COLOR)
    else:
        hexchat.prnt(color_name + ' is not a known color.')
        hexchat.prnt('Try: ' + COLOR_DEMO)

    return hexchat.EAT_ALL

def reset_mask_color(word, word_eol, userdata):
    combo = get_combo()

    if combo in PREFS.color_overrides:
        del PREFS.color_overrides[combo]
        hexchat.prnt('Color for {} has been reset'.format(combo))

    return hexchat.EAT_ALL

def toggle_mask_colors(word, word_eol, userdata):
    PREFS.color_messages = not PREFS.color_messages
 
def unmasked_message(word, word_eol, userdata):
    if len(word_eol) > 1:
        send(word_eol[1])

    return hexchat.EAT_ALL

def unload(userdata):
    try:
        with open(STATE_FILE_PATH, 'wb') as f:
            dump(PREFS, f)
    except Exception as e:
        hexchat.prnt(str(e))

    hexchat.prnt('{} unloaded'.format(__module_name__))

def init():
    hexchat.hook_command('mask', add_mask,
                         help='Usage: MASK <name>, sets mask for this channel')

    hexchat.hook_command('maskcolor', override_mask_color,
                         help='Usage: MASKCOLOR <color>, sets mask color to '
                         + 'one of ' + COLOR_DEMO)

    hexchat.hook_command('resetmaskcolor', reset_mask_color,
                         help='Resets mask color for this channel')

    hexchat.hook_command('togglemaskcolors', toggle_mask_colors,
                         help='Toggles mask colors in chat')

    hexchat.hook_command('unmask', remove_mask,
                         help='Removes mask for this channel')
 
    hexchat.hook_command('unmasked', unmasked_message,
                         help='Usage: UNMASKED <message>, sends message '
                         + 'without mask')

    hexchat.hook_command('', msg_hook)
    hexchat.hook_unload(unload)
    hexchat.prnt('Loaded {} {}'.format(__module_name__, __module_version__))

init()
