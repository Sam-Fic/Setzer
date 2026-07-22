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

from setzer.popovers.popover_manager import PopoverManager


class HeaderBar(object):
    '''组合持有 Adw.HeaderBar（Adw.HeaderBar 是 final 类型，不能被子类化）。

    所有子控件作为本 wrapper 的普通属性暴露，外部属性访问（preview_toggle /
    center_button / menu_button 等）零改动；唯一需要 .widget 前缀的是把
    headerbar 本身加进容器的调用（见 workspace_viewgtk add_top_bar）。
    '''

    def __init__(self):
        self.widget = Adw.HeaderBar()

        # sidebar toggles
        self.document_structure_toggle = Gtk.ToggleButton()
        self.document_structure_toggle.set_child(Gtk.Image(icon_name='document-structure-symbolic'))
        self.document_structure_toggle.set_can_focus(False)
        self.document_structure_toggle.set_tooltip_text(_('Toggle document structure') + ' (F2)')

        self.symbols_toggle = Gtk.ToggleButton()
        self.symbols_toggle.set_child(Gtk.Image(icon_name='insert-text-symbolic'))
        self.symbols_toggle.set_can_focus(False)
        self.symbols_toggle.set_tooltip_text(_('Toggle symbols') + ' (F3)')

        self.sidebar_toggles_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.sidebar_toggles_box.append(self.document_structure_toggle)
        self.sidebar_toggles_box.append(self.symbols_toggle)
        self.sidebar_toggles_box.add_css_class('linked')

        self.widget.pack_start(self.sidebar_toggles_box)

        # open document buttons
        self.open_document_blank_button = Gtk.Button.new_with_label(_('Open') + '...')
        self.open_document_blank_button.set_tooltip_text(_('Open a document') + ' (' + _('Ctrl') + '+O)')
        self.open_document_blank_button.set_action_name('win.open-document-dialog')

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.append(Gtk.Label(label=_('Open')))
        box.append(Gtk.Image(icon_name='pan-down-symbolic'))
        self.open_document_button = Gtk.MenuButton()
        self.open_document_button.set_child(box)
        self.open_document_button.set_can_focus(False)
        self.open_document_button.set_tooltip_text(_('Open a document') + ' (' + _('Shift') + '+' + _('Ctrl') + '+O)')
        self.open_document_button.set_popover(PopoverManager.get_popover('open_document').view.popover)

        # new document
        self.new_document_button = Gtk.MenuButton()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        box.append(Gtk.Image(icon_name='document-new-symbolic'))
        box.append(Gtk.Image(icon_name='pan-down-symbolic'))
        self.new_document_button.set_child(box)
        self.new_document_button.set_can_focus(False)
        self.new_document_button.set_tooltip_text(_('Create a new document'))
        self.new_document_button.set_popover(PopoverManager.get_popover('new_document').view.popover)

        self.widget.pack_start(self.open_document_button)
        self.widget.pack_start(self.open_document_blank_button)
        self.widget.pack_start(self.new_document_button)

        # workspace menu (standard Libadwaita main menu via Gio.Menu)
        self.hamburger = PopoverManager.create_popover('hamburger_menu')
        self.menu_button = self.hamburger.get_menu_button()
        self.menu_button.set_can_focus(False)

        # save document button (icon only)
        self.save_document_button = Gtk.Button(icon_name='document-save-symbolic')
        self.save_document_button.set_can_focus(False)
        self.save_document_button.set_tooltip_text(_('Save the current document') + ' (' + _('Ctrl') + '+S)')
        self.save_document_button.set_action_name('win.save')

        # help and preview toggles
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.preview_toggle = Gtk.ToggleButton()
        self.preview_toggle.set_child(Gtk.Image(icon_name='view-paged-symbolic'))
        self.preview_toggle.set_can_focus(False)
        self.preview_toggle.set_tooltip_text(_('Toggle preview') + ' (F9)')
        box.append(self.preview_toggle)
        self.help_toggle = Gtk.ToggleButton()
        self.help_toggle.set_child(Gtk.Image(icon_name='help-browser-symbolic'))
        self.help_toggle.set_can_focus(False)
        self.help_toggle.set_tooltip_text(_('Toggle help') + ' (F1)')
        box.append(self.help_toggle)
        box.add_css_class('linked')

        # build button wrapper (contains Save and Build / stop / clean / timer)
        self.build_wrapper = Gtk.CenterBox()
        self.build_wrapper.set_orientation(Gtk.Orientation.HORIZONTAL)

        # Right side, from the title outward: Save icon, preview/help toggles,
        # then the build group (whose leading button is "Save and Build"),
        # then the main menu. This puts "Save and Build" where the old textual
        # Save button was, and the icon-only Save where the build group was.
        self.widget.pack_end(self.menu_button)
        self.widget.pack_end(self.build_wrapper)
        self.widget.pack_end(box)
        self.widget.pack_end(self.save_document_button)

        # title / open documents popover
        self.open_docs_popover = PopoverManager.get_popover('document_switcher')

        # Adw.WindowTitle provides the title + subtitle (document name / folder)
        self.document_title = Adw.WindowTitle()
        self.document_title.set_title('')
        self.document_title.set_subtitle('')

        self.center_button = Gtk.MenuButton()
        self.center_button.set_tooltip_text(_('Show open documents') + ' (' + _('Ctrl') + '+T)')
        self.center_button.set_can_focus(False)
        self.center_button.set_child(self.document_title)
        self.center_button.set_valign(Gtk.Align.FILL)
        self.center_button.set_popover(self.open_docs_popover.view.popover)

        self.center_title_welcome = Adw.WindowTitle()
        self.center_title_welcome.set_title(_('Welcome to Setzer'))

        self.center_widget = Gtk.Stack()
        self.center_widget.set_valign(Gtk.Align.FILL)
        self.center_widget.add_named(self.center_button, 'button')
        self.center_widget.add_named(self.center_title_welcome, 'welcome')

        self.widget.set_title_widget(self.center_widget)
