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
# along with this program. If not to, see <http://www.gnu.org/licenses/>

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GObject, Adw, Pango

import time


class DocumentStructurePage(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.sections = dict()
        self.section_titles = list()
        self.scroll_to = None

        self.add_buttons()

        self.page = Adw.PreferencesPage()
        self.page.set_vexpand(True)
        # toolbar 已在 add_buttons() 内部 append 到 self，这里只追加 page
        self.append(self.page)

        # Adw.PreferencesPage 自身不暴露 get_vadjustment()，但其内部第一个
        # 子控件就是 Gtk.ScrolledWindow，从中取得 vadjustment 供滚动导航使用。
        self.scrolled_window = self.page.get_first_child()
        self.scrolled_window.get_vadjustment().connect('changed', self.on_scroll_or_resize)
        self.scrolled_window.get_vadjustment().connect('value-changed', self.on_scroll_or_resize)
        self.next_button.connect('clicked', self.on_next_button_clicked)
        self.prev_button.connect('clicked', self.on_prev_button_clicked)

    def add_section(self, name, title, widget):
        group = Adw.PreferencesGroup()
        group.set_title(title)
        group.add(widget)
        self.page.add(group)
        self.sections[name] = group
        self.section_titles.append(title)
        return group

    def set_section_visible(self, name, visible):
        self.sections[name].set_visible(visible)

    def add_buttons(self):
        # 顶部内嵌工具栏：左侧为随滚动更新的“当前分区”标题，右侧为
        # linked 的上一段 / 下一段导航按钮。两页（Document Structure /
        # Symbols）共享此结构，外观由 .sidebar-toolbar 统一。
        self.toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.toolbar.add_css_class('sidebar-toolbar')

        self.section_label = Gtk.Label(label='')
        self.section_label.add_css_class('dim-label')
        self.section_label.add_css_class('sidebar-section-title')
        self.section_label.set_halign(Gtk.Align.START)
        self.section_label.set_hexpand(True)
        self.section_label.set_xalign(0.0)
        self.section_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.section_label.set_margin_start(2)
        self.toolbar.append(self.section_label)

        self.nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.nav_box.add_css_class('linked')

        self.prev_button = Gtk.Button()
        self.prev_button.set_icon_name('go-up-symbolic')
        self.prev_button.set_tooltip_text(_('Previous section'))
        self.prev_button.add_css_class('flat')
        self.prev_button.set_can_focus(False)
        self.nav_box.append(self.prev_button)

        self.next_button = Gtk.Button()
        self.next_button.set_icon_name('go-down-symbolic')
        self.next_button.set_tooltip_text(_('Next section'))
        self.next_button.add_css_class('flat')
        self.next_button.set_can_focus(False)
        self.nav_box.append(self.next_button)

        self.toolbar.append(self.nav_box)
        self.append(self.toolbar)

    def on_scroll_or_resize(self, *args):
        scrolling_offset = self.scrolled_window.get_vadjustment().get_value()
        if scrolling_offset == 0:
            self.prev_button.set_sensitive(False)
        else:
            self.prev_button.set_sensitive(True)

        label_offsets = self.get_section_offsets()
        height_condition = scrolling_offset < self.page.get_allocated_height() - self.scrolled_window.get_allocated_height()
        label_condition = len(label_offsets) > 0 and scrolling_offset < label_offsets[-1]
        self.next_button.set_sensitive(height_condition and label_condition)

        self.update_section_label()

    def get_visible_sections(self):
        """返回 [(title, viewport_y), ...]，仅含当前可见的 group，按显示顺序。"""
        vadj = self.scrolled_window.get_vadjustment()
        scrolling_offset = vadj.get_value()
        result = list()
        groups = self.get_page_groups()
        for i, group in enumerate(groups):
            if not group.get_visible():
                continue
            title = self.section_titles[i] if i < len(self.section_titles) else group.get_title()
            y = group.get_allocation().y - scrolling_offset
            result.append((title, y))
        return result

    def get_section_offsets(self):
        return [y for (title, y) in self.get_visible_sections()]

    def get_current_section_title(self):
        """返回当前滚动到视口顶部的分区标题；视口顶部位于第一段之前时返回首段标题。"""
        sections = self.get_visible_sections()
        if len(sections) == 0:
            return ''
        current = sections[0][0]
        for title, y in sections:
            if y <= 1:
                current = title
            else:
                break
        return current

    def update_section_label(self):
        self.section_label.set_text(self.get_current_section_title())

    def get_page_groups(self):
        groups = list()
        child = self.page.get_first_child()
        while child is not None:
            groups.append(child)
            child = child.get_next_sibling()
        return groups

    def on_next_button_clicked(self, button):
        scrolling_offset = self.scrolled_window.get_vadjustment().get_value()

        for label_offset in self.get_section_offsets():
            if scrolling_offset < label_offset:
                self.scroll_view(label_offset)
                break

    def on_prev_button_clicked(self, button):
        scrolling_offset = self.scrolled_window.get_vadjustment().get_value()

        for label_offset in reversed([0] + self.get_section_offsets()):
            if scrolling_offset > label_offset:
                self.scroll_view(label_offset)
                break

    def scroll_view(self, position, duration=0.2):
        adjustment = self.scrolled_window.get_vadjustment()
        self.scroll_to = {'position_start': adjustment.get_value(), 'position_end': position, 'time_start': time.time(), 'duration': duration}
        self.scrolled_window.set_kinetic_scrolling(False)
        GObject.timeout_add(15, self.do_scroll)

    def do_scroll(self):
        if self.scroll_to != None:
            adjustment = self.scrolled_window.get_vadjustment()
            time_elapsed = time.time() - self.scroll_to['time_start']
            if self.scroll_to['duration'] == 0:
                time_elapsed_percent = 1
            else:
                time_elapsed_percent = time_elapsed / self.scroll_to['duration']
            if time_elapsed_percent >= 1:
                adjustment.set_value(self.scroll_to['position_end'])
                self.scroll_to = None
                self.scrolled_window.set_kinetic_scrolling(True)
                return False
            else:
                adjustment.set_value(self.scroll_to['position_start'] * (1 - self.ease(time_elapsed_percent)) + self.scroll_to['position_end'] * self.ease(time_elapsed_percent))
                return True
        return False

    def ease(self, time): return (time - 1)**3 + 1
