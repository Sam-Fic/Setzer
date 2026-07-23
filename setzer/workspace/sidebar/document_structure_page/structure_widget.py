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

        # 签名短路：populate() 调用 populate_if_changed(signature)，若签名与
        # 上次相同则跳过 clear_rows + 重建。按键在正文（不涉及 \section /
        # \label / \todo / \input）时，四个 section 的数据完全不变，签名命中，
        # 0 个 row 变动——这是打字卡顿的主要消除点。
        # 签名中包含 id(document)，确保文档切换时即便两文档结构恰好相同也强制重建。
        self._last_signature = None

    def on_row_activated(self, listbox, row):
        self.model.on_row_activated(row)

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
