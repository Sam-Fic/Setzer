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
from gi.repository import Gtk
from gi.repository import Adw
from gi.repository import GLib

from setzer.dialogs.document_wizard.pages.page import Page, PageView
from setzer.app.service_locator import ServiceLocator

import os
import re


class GeneralSettingsPage(Page):

    def __init__(self, current_values):
        self.current_values = current_values
        self.view = GeneralSettingsPageView()

    def observe_view(self):
        def text_changed(entry, field_name):
            self.current_values[field_name] = entry.get_text()

        def language_changed(combo, pspec):
            selected = combo.get_selected()
            if selected != Gtk.INVALID_LIST_POSITION:
                code = self.view.language_codes[selected]
                self.update_languages_list(code)

        def option_toggled(row, pspec, package_name):
            self.current_values['packages'][package_name] = row.get_active()

        self.view.title_entry.connect('changed', text_changed, 'title')
        self.view.author_entry.connect('changed', text_changed, 'author')
        self.view.date_entry.connect('changed', text_changed, 'date')

        self.view.language_combo.connect('notify::selected', language_changed)

        for name, row in self.view.option_packages.items():
            row.connect('notify::active', option_toggled, name)

    def load_presets(self, presets):
        try:
            text = presets['author']
        except TypeError:
            text = self.current_values['author']
        self.view.author_entry.set_text(text)
        self.view.title_entry.set_text('')
        self.view.date_entry.set_text('\\today')

        try:
            langs = presets['languages']
        except (TypeError, KeyError):
            langs = self.current_values['languages']
        self.current_values['languages'] = langs
        self.add_languages_list(langs)

        for name, option in self.view.option_packages.items():
            try:
                is_active = presets['packages'][name]
            except (TypeError, KeyError):
                is_active = self.current_values['packages'][name]
            option.set_active(is_active)

    def on_activation(self):
        self.view.title_entry.grab_focus()

    def add_languages_list(self, langs):
        model = Gtk.StringList()
        self.view.language_codes = list(langs.keys())
        for code in self.view.language_codes:
            model.append('{} ({})'.format(langs[code], code))
        self.view.language_combo.set_model(model)
        self.view.language_combo.set_selected(0)

    def update_languages_list(self, lang):
        dictionary = self.current_values['languages']

        if lang in dictionary and next(iter(dictionary)) != lang:
            value = dictionary.pop(lang)
            dictionary = {lang: value, **dictionary}

            self.current_values['languages'] = dictionary
            self.add_languages_list(dictionary)


class GeneralSettingsPageView(PageView):

    def __init__(self):
        PageView.__init__(self)

        self.header.set_text(_('General document settings'))
        self.headerbar_subtitle = _('Step') + ' 3: ' + _('General document settings')

        # Package descriptions (instance-level so gettext _() is resolved at
        # runtime, after gettext.install has run).
        self.package_descriptions = {
            'ams': _('<b>AMS packages:</b> provide mathematical symbols, math-related environments, …') + ' (' + _('recommended') + ')',
            'textcomp': '<b>textcomp:</b> ' + _('contains symbols to be used in textmode.') + ' (' + _('recommended') + ')',
            'graphicx': '<b>graphicx:</b> ' + _('include graphics in your document.') + ' (' + _('recommended') + ')',
            'color': '<b>color:</b> ' + _('foreground and background color.') + ' (' + _('recommended') + ')',
            'xcolor': '<b>xcolor:</b> ' + _('enables colored text.') + ' (' + _('recommended') + ')',
            'url': '<b>url:</b> ' + _('type urls with the \\url{..} command without escaping them.') + ' (' + _('recommended') + ')',
            'hyperref': '<b>hyperref:</b> ' + _('create hyperlinks within your document.'),
            'theorem': '<b>theorem:</b> ' + _('define theorem environments (like "definition", "lemma", …) with custom styling.'),
            'listings': '<b>listings:</b> ' + _('provides the \\listing environment for embedding programming code.'),
            'glossaries': '<b>glossaries:</b> ' + _('create a glossary for your document.'),
            'parskip': '<b>parskip:</b> ' + _('paragraphs without indentation.'),
        }

        # Document properties ------------------------------------------------
        self.group_document_properties = Adw.PreferencesGroup()
        self.group_document_properties.set_title(_('Document properties'))

        self.title_entry = Adw.EntryRow()
        self.title_entry.set_title(_('Title'))
        self.author_entry = Adw.EntryRow()
        self.author_entry.set_title(_('Author'))
        self.date_entry = Adw.EntryRow()
        self.date_entry.set_title(_('Date'))
        self.group_document_properties.add(self.title_entry)
        self.group_document_properties.add(self.author_entry)
        self.group_document_properties.add(self.date_entry)

        # Language -----------------------------------------------------------
        self.group_language = Adw.PreferencesGroup()
        self.group_language.set_title(_('Language'))
        self.group_language.set_description(_('The main language for this document. This is used to apply rules for hyphenation and other purposes.'))
        self.language_combo = Adw.ComboRow()
        self.language_combo.set_title(_('Language'))
        self.language_combo.set_model(Gtk.StringList())
        self.language_codes = list()
        self.group_language.add(self.language_combo)

        # Packages -----------------------------------------------------------
        self.option_packages = dict()
        self.option_packages['ams'] = self._create_package_row(_('AMS math packages'), 'ams')
        self.option_packages['textcomp'] = self._create_package_row('textcomp', 'textcomp')
        self.option_packages['graphicx'] = self._create_package_row('graphicx', 'graphicx')
        self.option_packages['color'] = self._create_package_row('color', 'color')
        self.option_packages['xcolor'] = self._create_package_row('xcolor', 'xcolor')
        self.option_packages['url'] = self._create_package_row('url', 'url')
        self.option_packages['hyperref'] = self._create_package_row('hyperref', 'hyperref')
        self.option_packages['theorem'] = self._create_package_row('theorem', 'theorem')
        self.option_packages['listings'] = self._create_package_row('listings', 'listings')
        self.option_packages['glossaries'] = self._create_package_row('glossaries', 'glossaries')
        self.option_packages['parskip'] = self._create_package_row('parskip', 'parskip')

        self.group_packages_left = Adw.PreferencesGroup()
        self.group_packages_left.set_title(_('Packages'))
        for name in ['ams', 'textcomp', 'graphicx', 'color', 'xcolor', 'url']:
            self.group_packages_left.add(self.option_packages[name])

        self.group_packages_right = Adw.PreferencesGroup()
        for name in ['hyperref', 'theorem', 'listings', 'glossaries', 'parskip']:
            self.group_packages_right.add(self.option_packages[name])

        # Layout -------------------------------------------------------------
        self.top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        self.top_row.append(self.group_document_properties)
        self.top_row.append(self.group_language)

        self.packages_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        self.packages_row.append(self.group_packages_left)
        self.packages_row.append(self.group_packages_right)

        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        self.content.append(self.top_row)
        self.content.append(self.packages_row)

        self.append(self.header)
        self.append(self.content)

    def _create_package_row(self, label, name):
        row = Adw.SwitchRow()
        row.set_title(label)
        row.set_tooltip_markup(self.package_descriptions[name])
        return row
