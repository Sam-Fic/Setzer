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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio


class NewDocumentView(object):

    def __init__(self):
        self.popover = Gtk.Popover()
        self.popover.set_size_request(252, -1)

        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.add_css_class('menu')

        self.popover.set_child(self.list_box)

        self.button_latex = self.create_row(_('New LaTeX Document'), 'win.new-latex-document')
        self.button_bibtex = self.create_row(_('New BibTeX Document'), 'win.new-bibtex-document')

        self.list_box.append(self.button_latex)
        self.list_box.append(self.button_bibtex)

        self.list_box.connect('row-activated', self.on_row_activated)

    def create_row(self, title, action_name):
        row = Adw.ActionRow()
        row.set_title(title)
        row.set_activatable(True)
        row.set_action_name(action_name)
        return row

    def on_row_activated(self, list_box, row):
        self.popover.popdown()
