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
from gi.repository import Gtk, Gdk

import setzer.workspace.sidebar.document_structure_page.todos_viewgtk as todos_section_view


class TodosSection(object):

    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.data_provider.connect('data_updated', self.update_items)

        self.view = todos_section_view.TodosSectionView(self)

        self.todos = list()

    def on_row_activated(self, row):
        todo = row.item_data
        if todo is None:
            return

        document = todo[2]
        line_number = document.source_buffer.get_iter_at_offset(todo[1]).get_line()
        self.data_provider.workspace.set_active_document(document)
        document.place_cursor(line_number)
        document.scroll_cursor_onscreen()
        self.data_provider.workspace.active_document.view.source_view.grab_focus()

    #@timer
    def update_items(self, *params):
        todos = list()
        document = self.data_provider.document
        for todo in document.parser.symbols['todos_with_offset']:
            # 不修改 parser 的 todo 列表（原 todo.append(document) 反复追加，
            # 每次更新都让列表增长）。构造新列表 [text, offset, document]。
            todos.append([todo[0], todo[1], document])
        for include_document in self.data_provider.integrated_includes:
            for todo in include_document.parser.symbols['todos_with_offset']:
                todos.append([todo[0], todo[1], include_document])
        todos.sort(key=lambda todo: todo[0].lower())
        self.todos = todos

        self.view.populate()
