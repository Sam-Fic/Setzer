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
# along with this program. If not see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

import os.path

from setzer.app.service_locator import ServiceLocator


class DocumentSwitcherView(object):

    def __init__(self):
        # 标准 Libadwaita 对话框：自带标题栏、Esc 关闭、自适应宽度。
        self.dialog = Adw.PreferencesDialog()
        self.dialog.set_title(_('Open Documents'))
        self.dialog.set_content_width(400)
        self.dialog.set_content_height(480)

        self.page = Adw.PreferencesPage()

        # 根文档说明：在 selection 模式下显示的描述 group。
        self.explaination_group = Adw.PreferencesGroup()
        self.explaination_label = Gtk.Label(label=_('Click on a document in the list below to set it as root. The root document will get built, no matter which document you are currently editing, and it will always display in the .pdf preview. The build log will also refer to the root document. This is often useful for working on large projects where typically a top level document (the root) will contain multiple lower level files via include statements.'))
        self.explaination_label.set_wrap(True)
        self.explaination_label.set_xalign(0)
        self.explaination_label.add_css_class('dim-label')
        self.explaination_label.add_css_class('caption')
        self.explaination_label.set_margin_top(6)
        self.explaination_label.set_margin_bottom(6)
        self.explaination_row = Gtk.ListBoxRow()
        self.explaination_row.set_child(self.explaination_label)
        self.explaination_row.set_activatable(False)
        self.explaination_row.set_selectable(False)
        self.explaination_group.add(self.explaination_row)
        self.explaination_group.set_visible(False)
        self.page.add(self.explaination_group)

        # 已打开文档列表：标准 Adw.PreferencesGroup + Adw.ActionRow。
        self.group = Adw.PreferencesGroup()
        self.page.add(self.group)

        # 底部动作：Set as Root / Unset Root（独立 PreferencesGroup + ActionRow）。
        self.root_group = Adw.PreferencesGroup()
        self.set_root_document_row = Adw.ActionRow()
        self.set_root_document_row.set_activatable(True)
        self.set_root_document_row.set_title(_('Set one Document as Root'))
        self.set_root_document_row.set_icon_name('document-properties-symbolic')
        self.root_group.add(self.set_root_document_row)

        self.unset_root_document_row = Adw.ActionRow()
        self.unset_root_document_row.set_activatable(True)
        self.unset_root_document_row.set_title(_('Unset Root Document'))
        self.unset_root_document_row.set_icon_name('document-edit-symbolic')
        self.root_group.add(self.unset_root_document_row)
        self.page.add(self.root_group)

        self.dialog.add(self.page)

        self.items = []
        self.rows = []

    def update_items(self, documents, root_selection_mode=False):
        visible_documents = [d for d in documents if (not root_selection_mode or d.is_latex_document())]
        visible_documents.sort(key=lambda val: -val.get_last_activated())

        for row in self.rows:
            self.group.remove(row)
        self.rows = []
        for document in visible_documents:
            row = self.create_row(document, root_selection_mode)
            self.group.add(row)
            self.rows.append(row)

    def create_row(self, document, root_selection_mode):
        row = Adw.ActionRow()
        row.set_activatable(True)
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
