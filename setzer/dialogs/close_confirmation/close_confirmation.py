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
from gi.repository import Adw

import os.path


class CloseConfirmationDialog(object):

    def __init__(self, main_window, workspace):
        self.main_window = main_window
        self.workspace = workspace
        self.parameters = None

    def run(self, parameters, callback):
        if parameters['unsaved_document'] == None: return

        self.parameters = parameters
        self.callback = callback

        self.setup(self.parameters['unsaved_document'])
        self.view.choose(self.main_window, None, self.dialog_process_response)

    def setup(self, document):
        self.view = Adw.AlertDialog(
            heading=_('Document »{document}« has unsaved changes.').format(document=document.get_displayname()),
            body=_('If you close without saving, these changes will be lost.'))
        self.view.add_response('discard', _('Close without Saving'))
        self.view.add_response('cancel', _('Cancel'))
        self.view.add_response('save', _('Save'))
        self.view.set_response_appearance('discard', Adw.ResponseAppearance.DESTRUCTIVE)
        self.view.set_response_appearance('save', Adw.ResponseAppearance.SUGGESTED)
        self.view.set_default_response('cancel')
        self.view.set_close_response('cancel')

    def dialog_process_response(self, dialog, result):
        response_id = dialog.choose_finish(result)
        # 映射回原数字语义，保持调用方契约兼容：
        # discard -> 0, cancel -> 1, save -> 2
        self.parameters['response'] = {'discard': 0, 'cancel': 1, 'save': 2}.get(response_id, 1)
        self.callback(self.parameters)
