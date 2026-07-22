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

import html


class KeyboardShortcutsDialog(object):

    def __init__(self, main_window):
        self.main_window = main_window

        data = list()

        section = {'title': _('Documents'), 'items': list()}
        section['items'].append({'title': _('Create new document'), 'shortcut': '<ctrl>N'})
        section['items'].append({'title': _('Open a document'), 'shortcut': '<ctrl>O'})
        section['items'].append({'title': _('Show recent documents'), 'shortcut': '<ctrl><shift>O'})
        section['items'].append({'title': _('Show open documents'), 'shortcut': '<ctrl>T'})
        section['items'].append({'title': _('Switch to the next open document'), 'shortcut': '<ctrl>Tab'})
        section['items'].append({'title': _('Save the current document'), 'shortcut': '<ctrl>S'})
        section['items'].append({'title': _('Save the document with a new filename'), 'shortcut': '<ctrl><shift>S'})
        section['items'].append({'title': _('Close the current document'), 'shortcut': '<ctrl>W'})
        data.append(section)

        section = {'title': _('Tools'), 'items': list()}
        section['items'].append({'title': _('Save and build .pdf-file from document'), 'shortcut': 'F5'})
        section['items'].append({'title': _('Build .pdf-file from document'), 'shortcut': 'F6'})
        section['items'].append({'title': _('Show current position in preview'), 'shortcut': 'F7'})
        data.append(section)

        section = {'title': _('Windows and Panels'), 'items': list()}
        section['items'].append({'title': _('Show help panel'), 'shortcut': 'F1'})
        section['items'].append({'title': _('Show build log'), 'shortcut': 'F8'})
        section['items'].append({'title': _('Show preview panel'), 'shortcut': 'F9'})
        section['items'].append({'title': _('Show global menu'), 'shortcut': 'F10'})
        section['items'].append({'title': _('Show context menu'), 'shortcut': 'F12'})
        section['items'].append({'title': _('Show keyboard shortcuts'), 'shortcut': '<ctrl>question'})
        section['items'].append({'title': _('Close Application'), 'shortcut': '<ctrl>Q'})
        data.append(section)

        section = {'title': _('Find and Replace'), 'items': list()}
        section['items'].append({'title': _('Find'), 'shortcut': '<ctrl>F'})
        section['items'].append({'title': _('Find the next match'), 'shortcut': '<ctrl>G'})
        section['items'].append({'title': _('Find the previous match'), 'shortcut': '<ctrl><shift>G'})
        section['items'].append({'title': _('Find and Replace'), 'shortcut': '<ctrl>H'})
        data.append(section)

        section = {'title': _('Zoom'), 'items': list()}
        section['items'].append({'title': _('Zoom in'), 'shortcut': '<ctrl>plus'})
        section['items'].append({'title': _('Zoom out'), 'shortcut': '<ctrl>minus'})
        section['items'].append({'title': _('Reset zoom'), 'shortcut': '<ctrl>0'})
        data.append(section)

        section = {'title': _('Copy and Paste'), 'items': list()}
        section['items'].append({'title': _('Copy selected text to clipboard'), 'shortcut': '<ctrl>C'})
        section['items'].append({'title': _('Cut selected text to clipboard'), 'shortcut': '<ctrl>X'})
        section['items'].append({'title': _('Paste text from clipboard'), 'shortcut': '<ctrl>V'})
        data.append(section)

        section = {'title': _('Undo and Redo'), 'items': list()}
        section['items'].append({'title': _('Undo previous text edit'), 'shortcut': '<ctrl>Z'})
        section['items'].append({'title': _('Redo previous text edit'), 'shortcut': '<ctrl><shift>Z'})
        data.append(section)

        section = {'title': _('Selection'), 'items': list()}
        section['items'].append({'title': _('Select all text'), 'shortcut': '<ctrl>A'})
        data.append(section)

        section = {'title': _('Editing'), 'items': list()}
        section['items'].append({'title': _('Toggle insert / overwrite'), 'shortcut': 'Insert'})
        section['items'].append({'title': _('Move current line up'), 'shortcut': '<Alt>Up'})
        section['items'].append({'title': _('Move current line down'), 'shortcut': '<Alt>Down'})
        section['items'].append({'title': _('Move current word left'), 'shortcut': '<Alt>Left'})
        section['items'].append({'title': _('Move current word right'), 'shortcut': '<Alt>Right'})
        section['items'].append({'title': _('Increment number at cursor'), 'shortcut': '<ctrl><shift>A'})
        section['items'].append({'title': _('Decrement number at cursor'), 'shortcut': '<ctrl><shift>X'})
        data.append(section)

        section = {'title': _('LaTeX Shortcuts'), 'items': list()}
        section['items'].append({'title': _('Comment / Uncomment current line(s)'), 'shortcut': '<ctrl>K'})
        section['items'].append({'title': _('New Line') + ' (\\\\)', 'shortcut': '<ctrl>Return'})
        section['items'].append({'title': _('Bold Text'), 'shortcut': '<ctrl>B'})
        section['items'].append({'title': _('Italic Text'), 'shortcut': '<ctrl>I'})
        section['items'].append({'title': _('Underlined Text'), 'shortcut': '<ctrl>U'})
        section['items'].append({'title': _('Typewriter Text'), 'shortcut': '<ctrl><shift>T'})
        section['items'].append({'title': _('Emphasized Text'), 'shortcut': '<ctrl><shift>E'})
        section['items'].append({'title': _('Quotation Marks'), 'shortcut': '<ctrl>quotedbl'})
        section['items'].append({'title': _('List Item'), 'shortcut': '<ctrl><shift>I'})
        section['items'].append({'title': _('Environment'), 'shortcut': '<ctrl>E'})
        data.append(section)

        section = {'title': _('Math Shortcuts'), 'items': list()}
        section['items'].append({'title': _('Inline Math Section'), 'shortcut': '<ctrl>M'})
        section['items'].append({'title': _('Display Math Section'), 'shortcut': '<ctrl><shift>M'})
        section['items'].append({'title': _('Equation'), 'shortcut': '<ctrl><shift>N'})
        section['items'].append({'title': _('Subscript'), 'shortcut': '<ctrl><shift>D'})
        section['items'].append({'title': _('Superscript'), 'shortcut': '<ctrl><shift>U'})
        section['items'].append({'title': _('Fraction'), 'shortcut': '<alt><shift>F'})
        section['items'].append({'title': '\\left', 'shortcut': '<ctrl><shift>L'})
        section['items'].append({'title': '\\right', 'shortcut': '<ctrl><shift>R'})
        data.append(section)

        self.data = data

    def run(self):
        self.setup()
        self.view.present(self.main_window)

    def setup(self):
        builder_string = '''<?xml version="1.0" encoding="UTF-8"?>
<interface>

  <object class="AdwShortcutsDialog" id="shortcuts-dialog">
'''

        for section in self.data:
            builder_string += '''    <child>
      <object class="AdwShortcutsSection">
        <property name="title" translatable="no">''' + html.escape(section['title']) + '''</property>
'''

            for item in section['items']:
                builder_string += '''        <child>
          <object class="AdwShortcutsItem">
            <property name="title" translatable="no">''' + html.escape(item['title']) + '''</property>
            <property name="accelerator">''' + html.escape(item['shortcut']) + '''</property>
          </object>
        </child>
'''

            builder_string += '''      </object>
    </child>
'''

        builder_string += '''  </object>

</interface>'''

        builder = Gtk.Builder.new_from_string(builder_string, -1)
        self.view = builder.get_object('shortcuts-dialog')
