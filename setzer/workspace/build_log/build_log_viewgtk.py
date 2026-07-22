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
from gi.repository import Gtk, GObject, Gio
from gi.repository import Pango

import os.path


# Map build-log item type to a symbolic icon name.
ICON_MAP = {
    'Error': 'dialog-error-symbolic',
    'Warning': 'dialog-warning-symbolic',
    'Badbox': 'own-badbox-symbolic',
}


class BuildLogItem(GObject.Object):
    '''A single build-log entry exposed to the Gtk.ListStore.

    Plain Python attributes are read by the factory's ``bind`` handler; the
    GObject base is required so instances can live in a ``Gio.ListStore``.
    '''

    def __init__(self, item_type, filename, line_number, description):
        GObject.Object.__init__(self)
        self.item_type = item_type
        self.filename = filename
        self.line_number = line_number
        self.description = description


class BuildLogView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.list = BuildLogList()

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_child(self.list)

        self.close_button = Gtk.Button(icon_name='window-close-symbolic')
        self.close_button.add_css_class('flat')
        self.close_button.set_can_focus(False)
        self.close_button.set_action_name('win.close-build-log')

        self.header_label = Gtk.Label()
        self.header_label.set_size_request(300, -1)
        self.header_label.set_xalign(0)
        self.header_label.set_margin_start(0)
        self.header_label.set_hexpand(True)

        self.header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.header.append(self.header_label)
        self.header.append(self.close_button)

        self.append(self.header)
        self.append(self.scrolled_window)
        self.set_size_request(200, 200)


class BuildLogList(Gtk.ListView):
    '''Native Gtk.ListView replacement for the former hand-drawn build log.

    Each row is a horizontal Box: [icon] [type] [file] [line] [description].
    Hover highlighting, scrolling and keyboard navigation come from the
    underlying Gtk.ListView; activation (single click) opens the source file
    at the reported line (wired in BuildLogController).
    '''

    def __init__(self):
        self.list_store = Gio.ListStore.new(BuildLogItem)
        self.selection = Gtk.SingleSelection(model=self.list_store)
        self.selection.set_can_unselect(True)
        Gtk.ListView.__init__(self, model=self.selection)
        self.set_single_click_activate(True)
        self.set_can_focus(False)

        self.factory = Gtk.SignalListItemFactory()
        self.factory.connect('setup', self.on_setup)
        self.factory.connect('bind', self.on_bind)
        self.set_factory(self.factory)

    def on_setup(self, factory, list_item):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.set_margin_start(12)
        row.set_margin_end(12)
        row.set_margin_top(3)
        row.set_margin_bottom(3)

        icon = Gtk.Image()
        icon.set_pixel_size(16)
        row.append(icon)

        type_label = Gtk.Label()
        type_label.set_xalign(0)
        type_label.set_width_chars(8)
        row.append(type_label)

        file_label = Gtk.Label()
        file_label.set_xalign(0)
        file_label.set_width_chars(18)
        file_label.set_ellipsize(Pango.EllipsizeMode.START)
        row.append(file_label)

        line_label = Gtk.Label()
        line_label.set_xalign(0)
        line_label.set_width_chars(8)
        row.append(line_label)

        desc_label = Gtk.Label()
        desc_label.set_xalign(0)
        desc_label.set_hexpand(True)
        desc_label.set_ellipsize(Pango.EllipsizeMode.END)
        row.append(desc_label)

        list_item.set_child(row)
        row.icon = icon
        row.type_label = type_label
        row.file_label = file_label
        row.line_label = line_label
        row.desc_label = desc_label

    def on_bind(self, factory, list_item):
        item = list_item.get_item()
        row = list_item.get_child()
        row.icon.set_from_icon_name(ICON_MAP.get(item.item_type, 'dialog-warning-symbolic'))
        row.type_label.set_label(item.item_type)
        row.file_label.set_label(os.path.basename(item.filename) if item.filename else '')
        if item.line_number >= 0:
            row.line_label.set_label(_('Line {number}').format(number=item.line_number))
        else:
            row.line_label.set_label('')
        row.desc_label.set_label(item.description)
