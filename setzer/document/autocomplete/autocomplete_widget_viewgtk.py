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
from gi.repository import Gtk, GLib


class AutocompleteWidgetView(Gtk.ListBox):
    '''Autocomplete popup listing up to 5 matching commands.

    Formerly a Gtk.DrawingArea with a custom Cairo draw function; now a
    standard Gtk.ListBox. The text view keeps keyboard focus (selection is
    driven by the model via the source view's key controller), so this
    widget is display-only: can_focus/can_target are disabled and the
    selected item is highlighted programmatically via select_row().
    '''

    def __init__(self, model):
        Gtk.ListBox.__init__(self)

        self.model = model

        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)
        self.set_can_focus(False)
        self.set_can_target(False)
        self.add_css_class('monospace')

    def populate(self):
        '''Rebuild the visible rows from the model's current state.

        Mirrors the former draw(): shows items[first:first+5], bolds the
        matched prefix (current_word) and renders dotlabels in place of the
        '•' placeholder at reduced alpha.
        '''
        model = self.model.model
        si = model.selected_item_index
        fi = model.first_item_index

        # Clear existing rows.
        child = self.get_first_child()
        while child is not None:
            sibling = child.get_next_sibling()
            self.remove(child)
            child = sibling

        if model.current_word is None or si is None or fi is None or len(model.items) == 0:
            return

        offset = len(model.current_word)
        selected_row = None
        for i, item in enumerate(model.items[fi:fi + 5]):
            command_text = '<b>' + GLib.markup_escape_text(item['command'][:offset]) + '</b>'
            command_text += GLib.markup_escape_text(item['command'][offset:])

            dotlabels = [d for d in item['dotlabels'].split('###') if d]
            for dotlabel in dotlabels:
                command_text = command_text.replace('•', '<span alpha="60%">' + GLib.markup_escape_text(dotlabel) + '</span>', 1)

            label = Gtk.Label()
            label.set_markup(command_text)
            label.set_halign(Gtk.Align.START)
            label.set_xalign(0.0)
            label.set_margin_start(6)
            label.set_margin_end(6)
            label.set_margin_top(2)
            label.set_margin_bottom(2)

            row = Gtk.ListBoxRow()
            row.set_child(label)
            row.set_activatable(False)
            row.set_selectable(True)
            self.append(row)

            if i == si - fi:
                selected_row = row

        if selected_row is not None:
            self.select_row(selected_row)
