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
from gi.repository import GLib
from gi.repository import Gio

from setzer.app.service_locator import ServiceLocator
from setzer.popovers.popover_manager import PopoverManager
from setzer.popovers.shortcutsbar.document_menu import DocumentMenu
from setzer.popovers.shortcutsbar.beamer_menu import BeamerMenu
from setzer.popovers.shortcutsbar.bibliography_menu import BibliographyMenu
from setzer.popovers.shortcutsbar.text_menu import TextMenu
from setzer.popovers.shortcutsbar.quotes_menu import QuotesMenu
from setzer.popovers.shortcutsbar.math_menu import MathMenu
from setzer.popovers.shortcutsbar.object_menu import ObjectMenu


class Shortcutsbar(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_can_focus(False)
        # 容器留白，强化"悬浮一排按钮"的视觉归属（无底板横条）
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_margin_start(6)
        self.set_margin_end(6)

        self.current_popover = None # popover being processed
        self.current_page = 'main' # page being processed

        self.top_icons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.top_icons.set_spacing(6)
        self.right_icons = Gtk.Box()
        self.right_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.right_icons.set_spacing(6)
        self.center_icons = Gtk.CenterBox()
        self.center_icons.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.center_icons.set_hexpand(True)

        self.italic_button = Gtk.Button()
        self.italic_button.set_icon_name('format-text-italic-symbolic')
        self.italic_button.set_action_name('win.insert-before-after')
        self.italic_button.set_action_target_value(GLib.Variant('as', ['\\textit{', '}']))
        self.italic_button.set_tooltip_text(_('Italic') + ' (' + _('Ctrl') + '+I)')
        self.top_icons.prepend(self.italic_button)

        self.bold_button = Gtk.Button()
        self.bold_button.set_icon_name('format-text-bold-symbolic')
        self.bold_button.set_action_name('win.insert-before-after')
        self.bold_button.set_action_target_value(GLib.Variant('as', ['\\textbf{', '}']))
        self.bold_button.set_tooltip_text(_('Bold') + ' (' + _('Ctrl') + '+B)')
        self.top_icons.prepend(self.bold_button)

        self.insert_quotes_button()

        self.insert_math_button()
        self.insert_text_button()
        self.insert_object_button()

        self.insert_bibliography_button()
        self.insert_beamer_button()
        self.insert_document_button()

        self.insert_wizard_button()

        self.button_search = Gtk.ToggleButton()
        self.button_search.set_icon_name('edit-find-symbolic')
        self.button_search.set_tooltip_text(_('Find') + ' (' + _('Ctrl') + '+F)')
        self.right_icons.append(self.button_search)

        self.button_replace = Gtk.ToggleButton()
        self.button_replace.set_icon_name('edit-find-replace-symbolic')
        self.button_replace.set_tooltip_text(_('Find and Replace') + ' (' + _('Ctrl') + '+H)')
        self.right_icons.append(self.button_replace)

        self.button_more = Gtk.MenuButton()
        self.button_more.set_icon_name('view-more-symbolic')
        self.button_more.set_popover(PopoverManager.create_popover('context_menu').view)
        self.button_more.set_tooltip_text(_('Context Menu') + ' (F12)')
        self.right_icons.append(self.button_more)

        self.button_build_log = Gtk.ToggleButton()
        self.button_build_log.set_icon_name('build-log-symbolic')
        self.button_build_log.set_tooltip_text(_('Build log') + ' (F8)')
        self.right_icons.append(self.button_build_log)

        self.append(self.top_icons)
        self.append(self.center_icons)
        self.append(self.right_icons)

    def insert_wizard_button(self):
        icon_widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon = Gtk.Image(icon_name='document-new-symbolic')
        icon.set_margin_start(4)
        icon_widget.append(icon)
        label = Gtk.Label(label=_('New Document Wizard'))
        label.set_margin_start(6)
        label.set_margin_end(4)
        self.wizard_button_revealer = Gtk.Revealer()
        self.wizard_button_revealer.set_child(label)
        self.wizard_button_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.wizard_button_revealer.set_reveal_child(True)
        icon_widget.append(self.wizard_button_revealer)

        self.wizard_button = Gtk.Button()
        self.wizard_button.set_tooltip_text(_('Create a template document'))
        self.wizard_button.set_can_focus(False)
        self.wizard_button.set_child(icon_widget)
        self.wizard_button.set_action_name('win.show-document-wizard')

        self.top_icons.prepend(self.wizard_button)

    def _setup_menu_button(self, button, menu_builder):
        '''Wire a Gio.Menu model to a Gtk.MenuButton and add the standard
        .menu CSS class to the auto-created Gtk.PopoverMenu — identical to
        how the hamburger menu is set up.'''
        button.set_menu_model(menu_builder.model)
        popover = button.get_popover()
        if popover is not None:
            popover.add_css_class('menu')

    def insert_document_button(self):
        self.document_button = Gtk.MenuButton()
        self.document_button.set_icon_name('application-x-addon-symbolic')
        self.document_button.set_tooltip_text(_('Document'))
        self._setup_menu_button(self.document_button, DocumentMenu())

        self.top_icons.prepend(self.document_button)

    def insert_beamer_button(self):
        self.beamer_button = Gtk.MenuButton()
        self.beamer_button.set_icon_name('view-list-bullet-symbolic')
        self.beamer_button.set_tooltip_text(_('Beamer'))
        self._setup_menu_button(self.beamer_button, BeamerMenu())

        self.top_icons.prepend(self.beamer_button)

    def insert_bibliography_button(self):
        self.bibliography_button = Gtk.MenuButton()
        self.bibliography_button.set_icon_name('library-symbolic')
        self.bibliography_button.set_tooltip_text(_('Bibliography'))
        self._setup_menu_button(self.bibliography_button, BibliographyMenu())

        self.top_icons.prepend(self.bibliography_button)

    def insert_text_button(self):
        self.text_button = Gtk.MenuButton()
        self.text_button.set_icon_name('text-symbolic')
        self.text_button.set_tooltip_text(_('Text'))
        self._setup_menu_button(self.text_button, TextMenu())

        self.top_icons.prepend(self.text_button)

    def insert_quotes_button(self):
        self.quotes_button = Gtk.MenuButton()
        self.quotes_button.set_icon_name('own-quotes-symbolic')
        self.quotes_button.set_tooltip_text(_('Quotes') + ' (' + _('Ctrl') + '+")')
        self._setup_menu_button(self.quotes_button, QuotesMenu())

        self.top_icons.prepend(self.quotes_button)

    def insert_math_button(self):
        self.math_button = Gtk.MenuButton()
        self.math_button.set_icon_name('own-math-menu-symbolic')
        self.math_button.set_tooltip_text(_('Math'))
        self._setup_menu_button(self.math_button, MathMenu())

        self.top_icons.prepend(self.math_button)

    def insert_object_button(self):
        self.insert_object_button = Gtk.MenuButton()
        self.insert_object_button.set_icon_name('insert-object-symbolic')
        self.insert_object_button.set_tooltip_text(_('Objects'))
        self._setup_menu_button(self.insert_object_button, ObjectMenu())

        self.top_icons.prepend(self.insert_object_button)


