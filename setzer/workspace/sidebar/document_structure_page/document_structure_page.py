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
from gi.repository import Gtk, GObject, Adw

import time


class DocumentStructurePage(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.sections = dict()
        self.scroll_to = None

        self.add_buttons()

        self.page = Adw.PreferencesPage()
        self.page.set_vexpand(True)
        # 注意：tabs_box 已在 add_buttons() 内部 append 到 self，这里只追加 page
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
        return group

    def set_section_visible(self, name, visible):
        self.sections[name].set_visible(visible)

    def add_buttons(self):
        self.tabs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.prev_button = Gtk.Button()
        self.prev_button.set_icon_name('go-up-symbolic')
        self.prev_button.set_tooltip_text(_('Back'))
        self.prev_button.add_css_class('flat')
        self.prev_button.set_can_focus(False)
        self.tabs.append(self.prev_button)

        self.next_button = Gtk.Button()
        self.next_button.set_icon_name('go-down-symbolic')
        self.next_button.set_tooltip_text(_('Forward'))
        self.next_button.add_css_class('flat')
        self.next_button.set_can_focus(False)
        self.tabs.append(self.next_button)

        self.tabs_box = Gtk.CenterBox()
        self.tabs_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.tabs_box.set_start_widget(Gtk.Label(label='Files'))
        self.tabs_box.set_end_widget(self.tabs)
        self.append(self.tabs_box)

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

    def get_section_offsets(self):
        vadj = self.scrolled_window.get_vadjustment()
        scrolling_offset = vadj.get_value()
        offsets = list()
        for group in self.get_page_groups():
            if not group.get_visible():
                continue
            y = group.get_allocation().y - scrolling_offset
            offsets.append(y)
        return offsets

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
