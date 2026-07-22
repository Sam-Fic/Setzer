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

from gi.repository import Gtk


class BuildLogController(object):

    def __init__(self, build_log, build_log_view):
        self.build_log = build_log
        self.view = build_log_view

        # Single-click activation on the Gtk.ListView drives row opening;
        # the former manual y->row math + hover tracking is gone (hover is now
        # native).
        self.view.list.connect('activate', self.on_row_activated)

    def on_row_activated(self, listview, position):
        if self.build_log.document == None:
            return

        item = listview.get_model().get_item(position)
        if item is None or item.filename is None:
            return

        self.build_log.workspace.open_document_by_filename(item.filename)
        line_number = item.line_number - 1
        if line_number < 0:
            return

        self.build_log.workspace.active_document.place_cursor(item.line_number - 1)
        self.build_log.workspace.active_document.scroll_cursor_onscreen()
        self.build_log.workspace.active_document.source_view.grab_focus()
