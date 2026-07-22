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
from gi.repository import Gtk

import os.path

from setzer.popovers.document_chooser.document_chooser_viewgtk import DocumentChooserView
from setzer.app.service_locator import ServiceLocator


class DocumentChooser(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = ServiceLocator.get_main_window()
        self.view = DocumentChooserView()

        self.workspace.connect('update_recently_opened_documents', self.on_update_recently_opened_documents)

        self.view.search_entry.connect('search-changed', self.on_document_chooser_search_changed)
        self.view.search_entry.connect('activate', self.on_search_activate)
        self.view.search_entry.connect('stop-search', self.on_stop_search)
        self.view.search_entry.connect('next-match', self.on_next_match)
        self.view.search_entry.connect('previous-match', self.on_previous_match)

        self.view.list_box.connect('row-activated', self.on_row_activated)

        self.view.other_documents_button.connect('clicked', self.on_other_docs_clicked)

        self.view.popover.connect('closed', self.on_popover_closed)

    def on_row_activated(self, list_box, row):
        if row == None: return
        folder = row.folder
        filename = row.filename
        self.view.popover.popdown()
        self.workspace.open_document_by_filename(folder + '/' + filename)

    def on_update_recently_opened_documents(self, workspace, recently_opened_documents):
        items = list()
        data = recently_opened_documents.values()
        for item in sorted(data, key=lambda val: -val['date']):
            items.append(os.path.split(item['filename']))
        self.view.update_items(items)

    def on_popover_closed(self, popover):
        self.view.search_entry.set_text('')
        active_document = self.workspace.get_active_document()
        if active_document != None:
            active_document.view.source_view.grab_focus()

    def on_document_chooser_search_changed(self, search_entry):
        self.view.search_filter()

    def on_search_activate(self, search_entry=None):
        selected = self.view.list_box.get_selected_row()
        if selected != None:
            self.on_row_activated(self.view.list_box, selected)

    def on_next_match(self, search_entry=None):
        self.select_visible_row(1)

    def on_previous_match(self, search_entry=None):
        self.select_visible_row(-1)

    def select_visible_row(self, direction):
        rows = [row for row in self.view.list_box if row.get_visible()]
        if len(rows) == 0: return
        selected = self.view.list_box.get_selected_row()
        if selected == None:
            self.view.list_box.select_row(rows[0])
            return
        index = rows.index(selected) + direction
        index = max(0, min(len(rows) - 1, index))
        self.view.list_box.select_row(rows[index])

    def on_stop_search(self, search_entry=None):
        self.view.popover.popdown()

    def on_other_docs_clicked(self, button):
        self.workspace.actions.actions['open-document-dialog'].activate()
        self.view.popover.popdown()
