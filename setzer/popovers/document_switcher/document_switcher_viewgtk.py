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

import os.path

from setzer.app.service_locator import ServiceLocator


class DocumentSwitcherView(object):

    def __init__(self):
        self.popover = Gtk.Popover()
        self.popover.set_size_request(414, -1)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.popover.set_child(self.box)

        self.root_explaination1 = Gtk.Label(label=_('Click on a document in the list below to set it as root.'))
        self.root_explaination1.set_margin_top(6)
        self.root_explaination1.set_xalign(0)
        self.root_explaination_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.root_explaination_box.append(self.root_explaination1)
        self.root_explaination2 = Gtk.Label(label=_('The root document will get built, no matter which document\nyou are currently editing, and it will always display in the .pdf\npreview. The build log will also refer to the root document.\nThis is often useful for working on large projects where typically\na top level document (the root) will contain multiple lower\nlevel files via include statements.'))
        self.root_explaination2.set_xalign(0)
        self.root_explaination2.set_margin_top(15)
        self.root_explaination2.set_margin_bottom(10)
        self.root_explaination_box.append(self.root_explaination2)
        self.root_explaination_revealer = Gtk.Revealer()
        self.root_explaination_revealer.set_child(self.root_explaination_box)
        self.root_explaination_revealer.set_reveal_child(False)
        self.box.append(self.root_explaination_revealer)

        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.add_css_class('boxed-list')

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.list_box)
        self.scrolled_window.set_min_content_height(120)
        self.scrolled_window.set_max_content_height(400)
        self.scrolled_window.set_propagate_natural_height(True)
        self.box.append(self.scrolled_window)

        self.set_root_document_button = Gtk.Button.new_with_label(_('Set one Document as Root'))
        self.set_root_document_button.set_can_focus(False)
        self.unset_root_document_button = Gtk.Button.new_with_label(_('Unset Root Document'))
        self.unset_root_document_button.set_can_focus(False)
        self.box.append(self.set_root_document_button)
        self.box.append(self.unset_root_document_button)

    def update_items(self, documents, root_selection_mode=False):
        self.list_box.remove_all()
        visible_documents = [d for d in documents if (not root_selection_mode or d.is_latex_document())]
        visible_documents.sort(key=lambda val: -val.get_last_activated())
        for document in visible_documents:
            row = self.create_row(document, root_selection_mode)
            self.list_box.append(row)

    def create_row(self, document, root_selection_mode):
        row = Adw.ActionRow()
        row.document = document

        doc_type = document.get_document_type()
        icon_name = {'latex': 'document-latex-symbolic',
                     'bibtex': 'document-bibtex-symbolic'}.get(doc_type, 'document-other-symbolic')
        icon = Gtk.Image(icon_name=icon_name)
        row.add_prefix(icon)

        modified_suffix = '*' if document.source_buffer.get_modified() else ''
        root_suffix = '  (root)' if document.get_is_root() else ''
        row.set_title(os.path.split(document.get_displayname())[1] + modified_suffix + root_suffix)

        close_button = Gtk.Button.new_from_icon_name('window-close-symbolic')
        close_button.set_has_frame(False)
        close_button.set_valign(Gtk.Align.CENTER)
        close_button.set_tooltip_text(_('Close document'))
        close_button.add_css_class('flat')
        close_button.row = row
        row.add_suffix(close_button)
        row.close_button = close_button

        if root_selection_mode and document.get_is_root():
            root_icon = Gtk.Image(icon_name='emblem-ok-symbolic')
            row.add_suffix(root_icon)

        return row
