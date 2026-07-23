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


class StructureWidget(Gtk.Box):
    '''Base class for the sidebar structure lists (structure/files/labels/todos).

    Formerly a Gtk.DrawingArea with a custom snapshot()/draw_nodes() that
    hand-painted icons, text and a hover background; now a standard Gtk.ListBox
    whose rows are Adw.ActionRow instances. Hover highlighting comes from the
    built-in row :hover state, and clicks are handled via the row-activated
    signal (delegated to the presenter's on_row_activated, which receives the
    row carrying an `item_data` payload).
    '''

    def __init__(self, model):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.model = model

        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list_box.set_activate_on_single_click(True)
        self.list_box.set_can_focus(False)
        self.list_box.set_hexpand(True)
        self.list_box.add_css_class('compact-rows')
        self.list_box.add_css_class('boxed-list')
        self.list_box.connect('row-activated', self.on_row_activated)
        Gtk.Box.append(self, self.list_box)

        self.empty_state = Adw.StatusPage()
        self.empty_state.set_visible(False)
        self.empty_state.set_vexpand(True)
        self.empty_state.add_css_class('compact')
        self.empty_state.add_css_class('sidebar-empty-state')
        Gtk.Box.append(self, self.empty_state)

        # 签名短路：populate() 调用 populate_if_changed(signature)，若签名与
        # 上次相同则跳过 clear_rows + 重建。按键在正文（不涉及 \section /
        # \label / \todo / \input）时，四个 section 的数据完全不变，签名命中，
        # 0 个 row 变动——这是打字卡顿的主要消除点。
        # 签名中包含 id(document)，确保文档切换时即便两文档结构恰好相同也强制重建。
        self._last_signature = None

    def on_row_activated(self, listbox, row):
        self.model.on_row_activated(row)

    def set_empty_state(self, icon_name, title, description=None):
        self.empty_state.set_icon_name(icon_name)
        self.empty_state.set_title(title)
        if description is not None:
            self.empty_state.set_description(description)

    def set_empty_state_visible(self, visible):
        self.set_visible(True)
        self.list_box.set_visible(not visible)
        self.empty_state.set_visible(visible)

    def populate_if_changed(self, signature):
        '''若 signature 与上次 populate 时相同，返回 False（调用方应跳过重建）；
        否则记录并返回 True（调用方继续重建）。首次调用必返回 True。'''
        if signature == self._last_signature:
            return False
        self._last_signature = signature
        return True

    def invalidate_signature(self):
        '''强制下次 populate 重建（用于文档切换等需要无条件刷新的场景）。'''
        self._last_signature = None

    def clear_rows(self):
        self._last_signature = None
        child = self.list_box.get_first_child()
        while child is not None:
            sibling = child.get_next_sibling()
            self.list_box.remove(child)
            child = sibling

    def append_row(self, row):
        self.list_box.append(row)

    def filter_rows(self, query):
        query = query.lower() if query else ''
        child = self.list_box.get_first_child()
        any_visible = False
        while child is not None:
            if isinstance(child, Adw.ActionRow):
                title = child.get_title() or ''
                match = not query or query in title.lower()
                child.set_visible(match)
                if match:
                    any_visible = True
            child = child.get_next_sibling()
        return any_visible

    def make_row(self, icon_name, text, indent):
        row = Adw.ActionRow()
        row.set_selectable(False)
        row.set_activatable(True)
        prefix_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        if indent > 0:
            spaces = '\u00A0' * (indent // 6)
            prefix_label = Gtk.Label(label=spaces)
            prefix_label.set_xalign(1.0)
            prefix_box.append(prefix_label)
        prefix_box.append(Gtk.Image(icon_name=icon_name))
        row.add_prefix(prefix_box)
        row.set_title(text)
        return row
