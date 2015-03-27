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

__module_name__ = "SwitchMask"
__module_version__ = "0.0"
__module_description__ = "Roleplaying nick switcher"
__module_author__ = "David McMackins II"

import hexchat

masks = {}

def add_mask(word, word_eol, userdata):
    channel = hexchat.get_info("channel")
    masks[channel] = word[1]
    hexchat.prnt("Mask set to " + word[1] + " for channel " + channel)
    return hexchat.EAT_ALL

def remove_mask(word, word_eol, userdata):
    channel = hexchat.get_info("channel")
    del masks[channel]
    hexchat.prnt("Removed mask for " + channel)
    return hexchat.EAT_ALL

def msg_hook(word, word_eol, userdata):
    channel = hexchat.get_info("channel")

    try:
        msg = "<{}> {}".format(masks[channel], word_eol[0])
    except KeyError:
        msg = word_eol[0]

    hexchat.command("MSG {} {}".format(channel, msg))
    return hexchat.EAT_ALL

def unload(userdata):
    hexchat.prnt("{} unloaded".format(__module_name__))

def init():
    hexchat.hook_command("mask", add_mask)
    hexchat.hook_command("unmask", remove_mask)
    hexchat.hook_command("", msg_hook)
    hexchat.hook_unload(unload)
    hexchat.prnt("Loaded {} {}".format(__module_name__, __module_version__))

init()
