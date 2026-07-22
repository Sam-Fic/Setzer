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


class FixedWidthLabel(Gtk.Label):
    '''A label with a fixed minimum width.

    Replaces the former Gtk.DrawingArea + Pango.Layout hand-drawing with a
    plain Gtk.Label, using set_size_request for the fixed width and
    set_xalign for horizontal alignment.
    '''

    def __init__(self, width):
        Gtk.Label.__init__(self)
        self.set_size_request(width, -1)
        self.set_xalign(0.5)
        self.set_halign(Gtk.Align.CENTER)
        self.set_justify(Gtk.Justification.CENTER)
        self.set_text('')
