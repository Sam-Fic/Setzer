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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Gio

from setzer.dialogs.dialog_locator import DialogLocator


class HamburgerMenu(object):

    def __init__(self, workspace):
        self.workspace = workspace
        self.main_window = self.workspace.main_window if hasattr(self.workspace, 'main_window') else None

        self.menu_model = Gio.Menu()

        self.build_static_items()
        self.build_session_submenu()

        self.register_actions()

        self.workspace.connect('update_recently_opened_session_files', self.on_update_recently_opened_session_files)

    def register_actions(self):
        main_window = ServiceLocator_get_main_window()
        # Restore Previous Session: open the session file chooser
        action_restore = Gio.SimpleAction.new('restore-session', None)
        action_restore.connect('activate', self.on_restore_session_click, None)
        main_window.add_action(action_restore)
        # Open a specific recent session file
        action_open = Gio.SimpleAction.new('open-session-file', GLib.VariantType('s'))
        action_open.connect('activate', self.on_restore_session_click)
        main_window.add_action(action_open)

    def build_static_items(self):
        self.menu_model.append(_('Save Document As…'), 'win.save-as')
        self.menu_model.append(_('Save All Documents'), 'win.save-all')

        self.menu_model.append_item(self.separator())

        self.session_section = Gio.Menu()
        session_item = Gio.MenuItem.new_submenu(_('Session'), self.session_section)
        self.menu_model.append_item(session_item)

        self.menu_model.append_item(self.separator())

        self.menu_model.append(_('Preferences'), 'win.show-preferences-dialog')

        self.menu_model.append_item(self.separator())

        shortcuts = Gio.MenuItem.new(_('Keyboard Shortcuts'), 'win.show-shortcuts-dialog')
        shortcuts.set_attribute_value('accel', GLib.Variant('s', '<Ctrl>question'))
        self.menu_model.append_item(shortcuts)
        self.menu_model.append(_('About'), 'win.show-about-dialog')

        self.menu_model.append_item(self.separator())

        self.menu_model.append(_('Close All Documents'), 'win.close-all-documents')
        close_doc = Gio.MenuItem.new(_('Close Document'), 'win.close-active-document')
        close_doc.set_attribute_value('accel', GLib.Variant('s', '<Ctrl>w'))
        self.menu_model.append_item(close_doc)
        quit_item = Gio.MenuItem.new(_('Quit'), 'win.quit')
        quit_item.set_attribute_value('accel', GLib.Variant('s', '<Ctrl>q'))
        self.menu_model.append_item(quit_item)

    @staticmethod
    def separator():
        item = Gio.MenuItem.new()
        item.set_attribute_value('role', GLib.Variant('s', 'separator'))
        return item

    def build_session_submenu(self):
        self.session_section.remove_all()
        self.session_section.append(_('Restore Previous Session…'), 'win.restore-session')
        self.session_section.append(_('Save Current Session…'), 'win.save-session')
        self.session_section.append_item(self.separator())
        self.recent_section = Gio.Menu()
        self.recent_item = Gio.MenuItem.new_section(_('Recent Sessions'), self.recent_section)
        self.session_section.append_item(self.recent_item)

    def on_update_recently_opened_session_files(self, workspace, recently_opened_session_files):
        self.recent_section.remove_all()
        items = list(recently_opened_session_files.values())
        for item in sorted(items, key=lambda val: -val['date']):
            filename = item['filename']
            menu_item = Gio.MenuItem.new(filename, 'win.open-session-file')
            menu_item.set_action_and_target_value('win.open-session-file', GLib.Variant('s', filename))
            self.recent_section.append_item(menu_item)

    def get_menu_button(self):
        button = Gtk.MenuButton()
        button.set_icon_name('open-menu-symbolic')
        button.set_tooltip_text(_('Main Menu') + ' (F10)')
        button.set_menu_model(self.menu_model)
        popover = button.get_popover()
        if popover is not None:
            popover.add_css_class('menu')
        return button

    def on_restore_session_click(self, action, parameter):
        if parameter is None:
            DialogLocator.get_dialog('open_session').run(self.restore_session_cb)
        else:
            filename = parameter.unpack()
            self.restore_session_cb(filename)

    def restore_session_cb(self, filename):
        if filename == None: return

        unsaved_documents = self.workspace.get_unsaved_documents()
        if len(unsaved_documents) > 0:
            self.workspace.set_active_document(unsaved_documents[0])
            dialog = DialogLocator.get_dialog('close_confirmation')
            dialog.run({'unsaved_document': unsaved_documents[0], 'session_filename': filename}, self.close_confirmation_cb)
        else:
            documents = self.workspace.get_all_documents()
            for document in documents:
                self.workspace.remove_document(document)
            self.workspace.load_documents_from_session_file(filename)

    def close_confirmation_cb(self, parameters):
        document = parameters['unsaved_document']

        if parameters['response'] == 0:
            self.workspace.remove_document(document)
            self.restore_session_cb(parameters['session_filename'])
        elif parameters['response'] == 2:
            if document.get_filename() == None:
                DialogLocator.get_dialog('save_document').run(document, self.restore_session_cb, parameters['session_filename'])
            else:
                document.save_to_disk()
                self.restore_session_cb(parameters['session_filename'])


def ServiceLocator_get_main_window():
    from setzer.app.service_locator import ServiceLocator
    return ServiceLocator.get_main_window()
