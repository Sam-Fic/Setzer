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
gi.require_versions({'Gtk': '4.0', 'WebKit': '6.0', 'Adw': '1'})
from gi.repository import WebKit, Gtk, Adw

from setzer.widgets.search_entry.search_entry import SearchEntry


class HelpPanelView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_size_request(396, -1)
        self.add_css_class('help')

        self.action_bar = Gtk.ActionBar()
        self.action_bar_left = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.action_bar_right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.action_bar.pack_start(self.action_bar_left)
        self.action_bar.pack_end(self.action_bar_right)

        self.home_button = Gtk.Button(icon_name='go-home-symbolic')
        self.home_button.set_tooltip_text(_('Home'))
        self.home_button.add_css_class('flat')
        self.home_button.set_can_focus(False)
        self.action_bar_left.append(self.home_button)

        self.up_button = Gtk.Button(icon_name='go-up-symbolic')
        self.up_button.set_tooltip_text(_('Top'))
        self.up_button.add_css_class('flat')
        self.up_button.set_can_focus(False)
        self.action_bar_left.append(self.up_button)

        self.back_button = Gtk.Button(icon_name='go-previous-symbolic')
        self.back_button.set_tooltip_text(_('Back'))
        self.back_button.add_css_class('flat')
        self.back_button.set_can_focus(False)
        self.action_bar_left.append(self.back_button)

        self.next_button = Gtk.Button(icon_name='go-next-symbolic')
        self.next_button.set_tooltip_text(_('Forward'))
        self.next_button.add_css_class('flat')
        self.next_button.set_can_focus(False)
        self.action_bar_left.append(self.next_button)

        self.search_button = Gtk.ToggleButton()
        self.search_button.set_icon_name('edit-find-symbolic')
        self.search_button.set_tooltip_text(_('Find'))
        self.search_button.add_css_class('flat')
        self.search_button.set_can_focus(False)
        self.action_bar_right.append(self.search_button)

        self.append(self.action_bar)

        # Search page: a single Adw.Clamp wraps the vertical search content,
        # giving native bounded/centered width. The entry sits at the top,
        # results scroll below, and a compact StatusPage shows the no-results
        # empty state. This replaces the former double-CenterBox floating blob.
        self.search_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.search_content_box.set_margin_top(12)
        self.search_content_box.set_margin_bottom(12)

        self.search_entry = SearchEntry()
        self.search_content_box.append(self.search_entry)

        self.search_results = Gtk.ListBox()
        self.search_results.set_selection_mode(Gtk.SelectionMode.NONE)
        self.search_results.set_can_focus(False)
        self.search_results.set_margin_top(12)
        self.search_scroll = Gtk.ScrolledWindow()
        self.search_scroll.set_vexpand(True)
        self.search_scroll.set_child(self.search_results)
        self.search_content_box.append(self.search_scroll)

        self.no_results_slate = Adw.StatusPage()
        self.no_results_slate.add_css_class('compact')
        self.no_results_slate.set_icon_name('system-search-symbolic')
        self.no_results_slate.set_title(_('No results found'))
        self.no_results_slate.set_visible(False)
        self.no_results_slate.set_vexpand(True)
        self.no_results_slate.set_valign(Gtk.Align.CENTER)
        self.search_content_box.append(self.no_results_slate)

        self.search_clamp = Adw.Clamp()
        self.search_clamp.set_maximum_size(600)
        self.search_clamp.set_tightening_threshold(400)
        self.search_clamp.set_child(self.search_content_box)

        self.content = WebKit.WebView()
        self.user_content_manager = self.content.get_user_content_manager()

        self.settings = self.content.get_settings()
        self.settings.set_enable_javascript(False)
        self.settings.set_enable_javascript_markup(False)
        self.settings.set_enable_developer_extras(False)
        self.settings.set_enable_page_cache(False)

        self.stack = Gtk.Stack()
        self.stack.set_vexpand(True)
        self.stack.add_named(self.content, 'content')
        self.stack.add_named(self.search_clamp, 'search')

        self.append(self.stack)

        self.search_result_items = list()


class SearchResultView(Gtk.ListBoxRow):

    def __init__(self, data):
        Gtk.ListBoxRow.__init__(self)
        self.set_can_focus(False)
        self.uri_ending = data[0]
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.set_margin_start(3)
        self.box.set_margin_end(3)
        self.text_label = Gtk.Label()
        self.text_label.set_markup(data[1])
        self.text_label.set_xalign(0)
        self.location_label = Gtk.Label()
        self.location_label.set_markup('' + data[2] + '')
        self.location_label.set_xalign(0)
        self.box.append(self.text_label)
        self.box.append(self.location_label)
        self.set_child(self.box)
