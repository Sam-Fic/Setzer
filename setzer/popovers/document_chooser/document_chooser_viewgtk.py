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


class DocumentChooserView(object):

    def __init__(self):
        self.popover = Gtk.Popover()
        self.popover.set_size_request(440, -1)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.popover.set_child(self.box)

        # 搜索框：左右及顶部留白，与 popover 边缘保持 12px 间距。
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_margin_start(12)
        self.search_entry.set_margin_end(12)
        self.search_entry.set_margin_top(12)
        self.search_entry.set_margin_bottom(6)
        self.box.append(self.search_entry)

        # 最近文档列表：boxed-list 自带圆角卡片外观，需与边缘保持 12px 间距。
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.set_activate_on_single_click(True)
        self.list_box.add_css_class('boxed-list')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.list_box)
        self.scrolled_window.set_min_content_height(240)
        self.scrolled_window.set_max_content_height(360)
        self.scrolled_window.set_propagate_natural_height(True)
        self.scrolled_window.set_margin_start(12)
        self.scrolled_window.set_margin_end(12)
        self.box.append(self.scrolled_window)

        # 无结果占位：libadwaita 紧凑状态页，仅在搜索无结果时显示。
        self.not_found_slate = Adw.StatusPage()
        self.not_found_slate.add_css_class('compact')
        self.not_found_slate.set_icon_name('system-search-symbolic')
        self.not_found_slate.set_title(_('No results'))
        self.not_found_slate.set_margin_start(12)
        self.not_found_slate.set_margin_end(12)
        self.not_found_slate.set_margin_top(6)
        self.not_found_slate.set_margin_bottom(6)
        self.box.append(self.not_found_slate)

        # 底部动作按钮：打开文件选择对话框，四周留白。
        self.other_documents_button = Gtk.Button.new_with_label(_('Other Documents') + '...')
        self.other_documents_button.set_can_focus(False)
        self.other_documents_button.set_margin_start(12)
        self.other_documents_button.set_margin_end(12)
        self.other_documents_button.set_margin_top(6)
        self.other_documents_button.set_margin_bottom(12)
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
        row = Adw.ActionRow()
        # 必须显式设为可激活，否则单击不会触发 ListBox::row-activated。
        row.set_activatable(True)
        row.folder = folder
        row.filename = filename
        row.set_title(filename)
        row.set_subtitle(folder)
        return row

    def search_filter(self):
        query = self.search_entry.get_text()
        query_lower = query.lower()
        count = 0
        for row in self.list_box:
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
