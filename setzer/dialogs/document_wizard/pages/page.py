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


class Page(object):

    def load_presets(self, presets):
        pass

    def on_activation(self):
        pass


class PageView(Gtk.Box):

    page_format_names = ['US Letter', 'US Legal', 'A4', 'A5', 'B5']

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.set_margin_start(18)
        self.set_margin_end(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)
        self.set_spacing(18)

        self.header = Gtk.Label(label='')
        self.header.set_xalign(0)
        self.header.add_css_class('title')

        self.headerbar_subtitle = ''

    def set_document_settings_page(self):
        '''Create the shared document-settings rows (page format, options,
        font size, margins) as libadwaita rows. Subclasses arrange them into
        PreferencesGroup sections and connect signals via their presenter.'''
        self.headerbar_subtitle = _('Step') + ' 2'

        # Page format -------------------------------------------------------
        self.page_format_combo = Adw.ComboRow()
        self.page_format_combo.set_title(_('Page format'))
        page_format_model = Gtk.StringList()
        for name in self.page_format_names:
            page_format_model.append(name)
        self.page_format_combo.set_model(page_format_model)

        # Options -----------------------------------------------------------
        self.option_landscape = Adw.SwitchRow()
        self.option_landscape.set_title(_('Landscape format'))

        self.option_twocolumn = Adw.SwitchRow()
        self.option_twocolumn.set_title(_('Two-column layout'))

        # Font size ---------------------------------------------------------
        # Gtk.Scale has no libadwaita equivalent, so it is kept and presented
        # as the suffix of an Adw.ActionRow for consistent row chrome.
        self.font_size_row = Adw.ActionRow()
        self.font_size_row.set_title(_('Font size'))
        self.font_size_entry = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 6, 18, 1)
        self.font_size_entry.set_draw_value(True)
        self.font_size_entry.set_hexpand(True)
        self.font_size_entry.set_valign(Gtk.Align.CENTER)
        self.font_size_entry.set_size_request(200, -1)
        self.font_size_row.add_suffix(self.font_size_entry)

        # Page margins ------------------------------------------------------
        self.option_default_margins = Adw.SwitchRow()
        self.option_default_margins.set_title(_('Use default margins'))

        self.margins_button_left = self._create_margin_row(_('Left'))
        self.margins_button_right = self._create_margin_row(_('Right'))
        self.margins_button_top = self._create_margin_row(_('Top'))
        self.margins_button_bottom = self._create_margin_row(_('Bottom'))

    def _create_margin_row(self, title):
        row = Adw.SpinRow()
        row.set_title(title)
        row.set_adjustment(Gtk.Adjustment(value=3.5, lower=0.0, upper=5.0, step_increment=0.1))
        row.set_digits(1)
        return row
