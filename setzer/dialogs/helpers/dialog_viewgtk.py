#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from setzer.keyboard_shortcuts.shortcut_controller import ShortcutController


class DialogView(Adw.Dialog):

    def __init__(self, main_window):
        Adw.Dialog.__init__(self)

        self.headerbar = Adw.HeaderBar()
        self.toolbar_view = Adw.ToolbarView()
        self.toolbar_view.add_top_bar(self.headerbar)

        self.topbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.toolbar_view.set_content(self.topbox)
        self.set_child(self.toolbar_view)

        self.shortcuts_controller = ShortcutController()
        self.shortcuts_controller.create_and_add_shortcut('Escape', self.close)
        self.add_controller(self.shortcuts_controller)
