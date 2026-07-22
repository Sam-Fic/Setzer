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
from gi.repository import Gtk


class Page(object):

    def load_presets(self, presets):
        pass

    def on_activation(self):
        pass


class PageView(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.add_css_class('document-wizard-page')

        self.set_margin_start(18)
        self.set_margin_top(18)
        self.set_margin_bottom(18)

        self.header = Gtk.Label(label='')
        self.header.set_xalign(0)
        self.header.set_margin_bottom(12)
        self.header.add_css_class('document-wizard-header')
        
        self.headerbar_subtitle = ''

    def set_document_settings_page(self):
        self.headerbar_subtitle = _('Step') + ' 2'
        self.content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.left_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.left_content.set_margin_end(20)
        self.right_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.right_content.set_margin_end(18)

        self.subheader_page_format = Gtk.Label(label=_('Page format'))
        self.subheader_page_format.add_css_class('document-wizard-subheader')
        self.subheader_page_format.set_xalign(0)

        self.page_format_list = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.page_format_list.set_margin_end(0)
        self.page_format_list.add_css_class('linked')

        self.page_format_buttons = dict()
        first_button = None
        for name in ['US Letter', 'US Legal', 'A4', 'A5', 'B5']:
            button = Gtk.CheckButton()
            button.set_label(name)
            button.set_margin_end(18)
            if first_button == None: first_button = button
            else: button.set_group(first_button)

            self.page_format_buttons[name] = button
            self.page_format_list.append(button)

        self.option_landscape = Gtk.CheckButton(label=_('Landscape format'))

        self.subheader_margins = Gtk.Label(label=_('Page margins'))
        self.subheader_margins.add_css_class('document-wizard-subheader')
        self.subheader_margins.set_xalign(0)
        self.subheader_margins.set_margin_top(18)
        self.option_default_margins = Gtk.CheckButton(label=_('Use default margins'))
        self.option_default_margins.set_margin_bottom(3)

        self.margins_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.margins_button_left = Gtk.SpinButton.new_with_range(0.0, 5.0, 0.1)
        self.margins_button_left.add_css_class('left')
        self.margins_button_right = Gtk.SpinButton.new_with_range(0.0, 5.0, 0.1)
        self.margins_button_right.add_css_class('right')
        self.margins_button_top = Gtk.SpinButton.new_with_range(0.0, 5.0, 0.1)
        self.margins_button_top.add_css_class('top')
        self.margins_button_bottom = Gtk.SpinButton.new_with_range(0.0, 5.0, 0.1)
        self.margins_button_bottom.add_css_class('bottom')
        self.margins_hbox1 = Gtk.CenterBox()
        self.margins_hbox1.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.margins_hbox1.set_center_widget(self.margins_button_top)
        self.margins_hbox2 = Gtk.CenterBox()
        self.margins_hbox2.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.margins_hbox2.set_start_widget(self.margins_button_left)
        self.margins_hbox2.set_end_widget(self.margins_button_right)
        self.margins_hbox3 = Gtk.CenterBox()
        self.margins_hbox3.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.margins_hbox3.set_center_widget(self.margins_button_bottom)
        self.margins_box.append(self.margins_hbox1)
        self.margins_box.append(self.margins_hbox2)
        self.margins_box.append(self.margins_hbox3)
        self.margins_box.add_css_class('margins-box')
        self.margins_box.set_size_request(348, -1)

        self.margins_description = Gtk.Label(label=_('All values are in cm (1 inch ≅ 2.54 cm).'))
        self.margins_description.set_xalign(0)
        self.margins_description.set_margin_top(6)
        self.margins_description.add_css_class('document-wizard-desc')

        self.subheader_font_size = Gtk.Label(label=_('Font size'))
        self.subheader_font_size.add_css_class('document-wizard-subheader')
        self.subheader_font_size.set_xalign(0)
        self.subheader_font_size.set_size_request(348, -1)
        self.subheader_font_size.set_margin_top(18)

        self.font_size_entry = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 6, 18, 1)
        self.font_size_entry.set_draw_value(True)

        self.subheader_options = Gtk.Label(label=_('Options'))
        self.subheader_options.add_css_class('document-wizard-subheader')
        self.subheader_options.set_xalign(0)
        self.subheader_options.set_margin_top(18)

        self.option_twocolumn = Gtk.CheckButton(label=_('Two-column layout'))


