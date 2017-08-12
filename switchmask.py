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
__module_version__ = '3.2.1'
__module_description__ = 'Roleplaying character name switcher'
__module_author__ = 'David McMackins II'

import hexchat

BOLD = '\x02'
COLOR = '\x03'
GRAY_COLOR = '14'
MSG_LEN = 466

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

color_messages = True
color_overrides = {}
colors = {}
masks = {}

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

    try:
        mask = word_eol[1]

        masks[combo] = mask
        colors[combo] = get_color(mask)
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

def recolor_msg(msg):
    parts = msg.split()
    last_color = COLOR
    size = 0
    out = ''
    for part in parts:
        if size + len(part) + 3 >= MSG_LEN:
            part = COLOR + last_color + part
            size = 0

        if COLOR in part:
            i = len(part) - part[::-1].index(COLOR) - 1
            last_color = part[i+1:i+3]

        out += part + ' '
        size += len(part) + 1

    return out.rstrip()

def msg_hook(word, word_eol, userdata):
    combo = get_combo()
    payload = word_eol[0]

    if combo not in masks:
        return hexchat.EAT_NONE

    mask = masks[combo]

    if color_messages:
        if combo in color_overrides:
            mask_color = color_overrides[combo]
        else:
            mask_color = colors[combo]

        payload = format_payload(mask_color, payload)
        mask = COLOR + COLOR + '<' + BOLD + COLOR + mask_color + mask + COLOR + BOLD + '>'
    else:
        mask = '<' + mask + '>'

    msg = '{} {}'.format(mask, payload)

    if color_messages:
        msg = recolor_msg(msg)

    send(msg)
    return hexchat.EAT_ALL

def override_mask_color(word, word_eol, userdata):
    if len(word_eol) != 2:
        hexchat.prnt('USAGE: /' + word[0] + ' <color>')
        hexchat.prnt('Colors: ' + COLOR_DEMO)
        return hexchat.EAT_ALL

    color_name = word_eol[1].strip()

    try:
        color = color_name_lookup(color_name)
        combo = get_combo()
        color_overrides[combo] = color
        hexchat.prnt('Color for ' + combo + ' set to ' + COLOR + color
                     + color_name + COLOR)
    except ValueError:
        hexchat.prnt(color_name + ' is not a known color.')
        hexchat.prnt('Try: ' + COLOR_DEMO)

    return hexchat.EAT_ALL

def reset_mask_color(word, word_eol, userdata):
    combo = get_combo()

    try:
        del color_overrides[combo]
    except KeyError:
        pass

    hexchat.prnt('Color for {} has been reset'.format(combo))
    return hexchat.EAT_ALL
 
def unmasked_message(word, word_eol, userdata):
    if len(word_eol) > 1:
        send(word_eol[1])

    return hexchat.EAT_ALL

def unload(userdata):
    hexchat.prnt('{} unloaded'.format(__module_name__))

def init():
    hexchat.hook_command('mask', add_mask,
                         help='Usage: MASK <name>, sets mask for this channel')

    hexchat.hook_command('maskcolor', override_mask_color,
                         help='Usage: MASKCOLOR <color>, sets mask color to '
                         + 'one of ' + COLOR_DEMO)

    hexchat.hook_command('resetmaskcolor', reset_mask_color,
                         help='Resets mask color for this channel')

    hexchat.hook_command('unmask', remove_mask,
                         help='Removes mask for this channel')
 
    hexchat.hook_command('unmasked', unmasked_message,
                         help='Usage: UNMASKED <message>, sends message '
                         + 'without mask')

    hexchat.hook_command('', msg_hook)
    hexchat.hook_unload(unload)
    hexchat.prnt('Loaded {} {}'.format(__module_name__, __module_version__))

init()
