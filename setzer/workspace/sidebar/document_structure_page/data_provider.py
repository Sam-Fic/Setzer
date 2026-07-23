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

import time
import os.path

from gi.repository import GLib

from setzer.helpers.observable import Observable
import setzer.helpers.path as path_helpers


class DataProvider(Observable):

    def __init__(self, sidebar, workspace):
        Observable.__init__(self)

        self.workspace = workspace
        self.document = None

        self.integrated_includes = dict()

        # data_updated 去抖：on_buffer_changed 可能在同一帧内被多次触发
        # （含被 include 的文档），用 idle 合并为一次重建，避免按键期间侧边栏
        # 四个 section 反复 clear_rows + 重建 Adw.ActionRow。
        self._update_data_idle_id = None

        self.signal_id = sidebar.view.connect('realize', self.on_realize)
        self.workspace.connect('new_document', self.on_new_document)
        self.workspace.connect('document_removed', self.on_document_removed)
        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('root_state_change', self.on_root_state_change)

    def on_new_document(self, workspace, document=None):
        self.update_data()

    def on_document_removed(self, workspace, document=None):
        self.update_data()

    def on_new_active_document(self, workspace, document=None):
        self.set_document()

    def on_root_state_change(self, workspace, root_state=None):
        self.set_document()

    def on_buffer_changed(self, document, parameter=None):
        # 去抖：同一帧内的多次 changed 合并为一次 update_data，避免按键期间
        # 侧边栏四个 section 反复全量重建。set_document 仍走同步路径，因此
        # 文档切换/首次加载的响应不受影响。
        if self._update_data_idle_id is None:
            self._update_data_idle_id = GLib.idle_add(self._update_data_idle)

    def _update_data_idle(self):
        self._update_data_idle_id = None
        self.update_data()
        return False

    def on_is_root_changed(self, document, parameter=None):
        self.update_data()

    def on_realize(self, view, *parameter):
        view.disconnect(self.signal_id)
        self.update_data()

    def set_document(self):
        document = self.workspace.get_root_or_active_latex_document()
        if document != self.document:
            if self.document != None:
                self.document.disconnect('changed', self.on_buffer_changed)
                self.document.disconnect('is_root_changed', self.on_is_root_changed)
            self.document = document
            if self.document != None:
                self.document.connect('changed', self.on_buffer_changed)
                self.document.connect('is_root_changed', self.on_is_root_changed)
            self.update_data()

    def update_data(self, *params):
        if self.document == None: return

        self.update_integrated_includes()
        self.add_change_code('data_updated')

    def update_integrated_includes(self):
        integrated_includes = dict()
        if self.document.get_is_root():
            for filename, offset in self.document.parser.symbols['included_latex_files']:
                filename = path_helpers.get_abspath(filename, self.document.get_dirname())
                document = self.workspace.get_document_by_filename(filename)
                if document:
                    integrated_includes[document] = (document, offset)

        # 仅连接新加入的文档，避免重复 connect（修复信号泄漏：原实现每次调用
        # 都对仍包含的文档叠加连接，导致一次文本改动触发 N 次侧边栏重建）。
        for document in integrated_includes:
            if document not in self.integrated_includes:
                document.connect('changed', self.on_buffer_changed)
        for document in self.integrated_includes:
            if document not in integrated_includes:
                try:
                    document.disconnect('changed', self.on_buffer_changed)
                except Exception:
                    pass
        self.integrated_includes = integrated_includes

    def get_includes(self):
        includes = list()
        for filename, offset in self.document.parser.symbols['included_latex_files']:
            filename = path_helpers.get_abspath(filename, self.document.get_dirname())
            document = self.workspace.get_document_by_filename(filename)
            if document and document in self.integrated_includes:
                includes.append({'filename': filename, 'offset': offset, 'document': document})
            else:
                includes.append({'filename': filename, 'offset': offset, 'document': None})
        return includes


