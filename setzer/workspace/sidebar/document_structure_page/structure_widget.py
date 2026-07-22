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
from gi.repository import Gtk, Adw


class StructureWidget(Gtk.ListBox):
    '''Base class for the sidebar structure lists (structure/files/labels/todos).

    Formerly a Gtk.DrawingArea with a custom snapshot()/draw_nodes() that
    hand-painted icons, text and a hover background; now a standard Gtk.ListBox
    whose rows are Adw.ActionRow instances. Hover highlighting comes from the
    built-in row :hover state, and clicks are handled via the row-activated
    signal (delegated to the presenter's on_row_activated, which receives the
    row carrying an `item_data` payload).
    '''

    def __init__(self, model):
        Gtk.ListBox.__init__(self)

        self.model = model

        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.set_activate_on_single_click(True)
        self.set_can_focus(False)
        self.connect('row-activated', self.on_row_activated)

    def on_row_activated(self, listbox, row):
        self.model.on_row_activated(row)

    def clear_rows(self):
        child = self.get_first_child()
        while child is not None:
            sibling = child.get_next_sibling()
            self.remove(child)
            child = sibling

    def make_row(self, icon_name, text, indent):
        row = Adw.ActionRow()
        row.set_selectable(False)
        row.set_activatable(True)
        row.add_prefix(Gtk.Image(icon_name=icon_name))
        row.set_title(text)
        row.set_margin_start(9 + indent)
        return row
