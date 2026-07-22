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
from gi.repository import Gtk, Pango


class DocumentChooserView(object):

    def __init__(self):
        self.popover = Gtk.Popover()
        self.popover.set_size_request(414, -1)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.popover.set_child(self.box)

        self.search_entry = Gtk.SearchEntry()
        self.box.append(self.search_entry)

        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.set_activate_on_single_click(True)
        self.list_box.add_css_class('menu')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.list_box)
        self.scrolled_window.set_min_content_height(240)
        self.scrolled_window.set_max_content_height(360)
        self.scrolled_window.set_propagate_natural_height(True)
        self.box.append(self.scrolled_window)

        self.not_found_slate = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.not_found_slate.set_margin_top(24)
        self.not_found_slate.set_margin_bottom(24)
        image = Gtk.Image(icon_name='system-search-symbolic')
        image.set_pixel_size(64)
        self.not_found_slate.append(image)
        self.not_found_slate.append(Gtk.Label(label=_('No results')))
        self.box.append(self.not_found_slate)

        self.other_documents_button = Gtk.Button.new_with_label(_('Other Documents') + '...')
        self.other_documents_button.set_can_focus(False)
        self.box.append(self.other_documents_button)

        self.items = []

    def update_items(self, items):
        self.items = []
        for folder, filename in items:
            self.items.append((folder, filename))

        self.list_box.remove_all()
        for folder, filename in self.items:
            row = self.create_row(folder, filename)
            self.list_box.append(row)
        self.search_filter()

    def create_row(self, folder, filename):
        row = Gtk.ListBoxRow()
        row.folder = folder
        row.filename = filename

        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        hbox.set_margin_start(12)
        hbox.set_margin_end(12)
        hbox.set_margin_top(8)
        hbox.set_margin_bottom(8)

        filename_label = Gtk.Label()
        filename_label.set_halign(Gtk.Align.START)
        filename_label.set_ellipsize(Pango.EllipsizeMode.START)
        filename_label.set_markup(filename)
        hbox.append(filename_label)
        row.filename_label = filename_label

        folder_label = Gtk.Label()
        folder_label.set_halign(Gtk.Align.START)
        folder_label.set_ellipsize(Pango.EllipsizeMode.START)
        folder_label.add_css_class('dim-label')
        folder_label.set_markup(folder)
        hbox.append(folder_label)
        row.folder_label = folder_label

        row.set_child(hbox)
        return row

    def search_filter(self):
        query = self.search_entry.get_text()
        query_lower = query.lower()
        count = 0
        for row in self.list_box:
            self.apply_highlight(row, query)
            match = (query == '' or
                     query_lower in row.filename.lower() or
                     query_lower in row.folder.lower())
            row.set_visible(match)
            if match:
                count += 1

        has_items = len(self.items) > 0
        self.not_found_slate.set_visible(count == 0 and has_items)
        self.scrolled_window.set_visible(count > 0)
        return count

    def apply_highlight(self, row, query):
        if query == '':
            row.filename_label.set_markup(row.filename)
            row.folder_label.set_markup(row.folder)
            return
        row.filename_label.set_markup(self.highlight(row.filename, query))
        row.folder_label.set_markup(self.highlight(row.folder, query))

    def highlight(self, text, query):
        import re
        result = ''
        counter = 0
        for pos in re.finditer(re.escape(query.lower()), text.lower()):
            result += text[:pos.start() + counter] + '<b>' + text[pos.start() + counter:pos.end() + counter] + '</b>' + text[pos.end() + counter:]
            counter += 7
        return result if result else text
