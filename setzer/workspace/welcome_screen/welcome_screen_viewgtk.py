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
from gi.repository import Gtk


class WelcomeScreenView(Gtk.Box):
    '''Welcome screen shown when no document is open.

    Replaces the former Gtk.Overlay + DrawingArea rotating-text animation
    (decorative lorem ipsum rendered at alpha=0.065, effectively invisible)
    with a simple centered vertical box using standard title/subtitle
    libadwaita text style classes.
    '''

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_spacing(12)

        self.header = Gtk.Label(label=_('Write beautiful LaTeX documents with ease!'))
        self.header.set_wrap(True)
        self.header.add_css_class('title')
        self.append(self.header)

        self.description = Gtk.Label(label=_('Click the open or create buttons in the headerbar above to start editing.'))
        self.description.set_wrap(True)
        self.description.add_css_class('subtitle')
        self.append(self.description)
