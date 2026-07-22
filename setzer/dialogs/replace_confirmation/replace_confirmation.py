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
gi.require_version('Adw', '1')
from gi.repository import Adw


class ReplaceConfirmationDialog(object):

    def __init__(self, main_window):
        self.main_window = main_window
        self.search_context = None
        self.replacement = None

    def run(self, original, replacement, number_of_occurrences, search_context):
        self.search_context = search_context
        self.replacement = replacement
        self.setup(original, replacement, number_of_occurrences)
        self.view.choose(self.main_window, None, self.dialog_process_response)

    def setup(self, original, replacement, number_of_occurrences):
        str_occurrences = ngettext('Replacing {amount} occurence of »{original}« with »{replacement}«.', 'Replacing {amount} occurrences of »{original}« with »{replacement}«.', number_of_occurrences)
        self.view = Adw.AlertDialog(
            heading=str_occurrences.format(amount=str(number_of_occurrences), original=original, replacement=replacement),
            body=_('Do you really want to do this?'))
        self.view.add_response('cancel', _('Cancel'))
        self.view.add_response('replace', _('Yes, replace all occurrences'))
        self.view.set_response_appearance('replace', Adw.ResponseAppearance.SUGGESTED)
        self.view.set_default_response('replace')
        self.view.set_close_response('cancel')

    def dialog_process_response(self, dialog, result):
        response_id = dialog.choose_finish(result)
        if response_id == 'replace':
            self.search_context.replace_all(self.replacement, -1)
