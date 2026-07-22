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

from setzer.popovers.helpers.standard_popover import StandardMenuViewBase


class ContextMenuView(StandardMenuViewBase):
    '''Shortcutsbar "more" popover (the F12 context menu).

    Migrated from the hand-built Popover(Gtk.Box) to StandardMenuViewBase,
    which wraps a Gtk.Popover + Gtk.ListBox with native keyboard navigation.
    Action items use add_action_button (returns the ListBoxRow so the
    presenter can toggle visibility of comment/sync/separator as a unit).
    '''

    def __init__(self, popover_manager):
        StandardMenuViewBase.__init__(self)

        self.set_width(288)

        self.add_action_button('main', _('Undo'), 'win.undo', shortcut=_('Ctrl') + '+Z')
        self.add_action_button('main', _('Redo'), 'win.redo', shortcut=_('Shift') + '+' + _('Ctrl') + '+Z')
        self.add_separator('main')
        self.add_action_button('main', _('Cut'), 'win.cut', shortcut=_('Ctrl') + '+X')
        self.add_action_button('main', _('Copy'), 'win.copy', shortcut=_('Ctrl') + '+C')
        self.add_action_button('main', _('Paste'), 'win.paste', shortcut=_('Ctrl') + '+V')
        self.add_action_button('main', _('Delete'), 'win.delete-selection')
        self.add_separator('main')
        self.add_action_button('main', _('Select All'), 'win.select-all', shortcut=_('Ctrl') + '+A')
        self.add_separator('main')
        self.comment_button = self.add_action_button('main', _('Toggle Comment'), 'win.toggle-comment', shortcut=_('Ctrl') + '+K')
        self.sync_button = self.add_action_button('main', _('Show in Preview'), 'win.forward-sync')
        self.latex_buttons_separator = self.add_separator('main')

        # Zoom row: label on the left, zoom-out / reset / zoom-in on the right.
        # These buttons trigger actions but must NOT close the popover (the user
        # may zoom repeatedly), so they live in a non-activatable custom row.
        box = Gtk.CenterBox()
        box.set_orientation(Gtk.Orientation.HORIZONTAL)
        zoom_label = Gtk.Label(label=_('Zoom'))
        zoom_label.set_margin_start(12)
        box.set_start_widget(zoom_label)
        inner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        button_zoom_out = Gtk.Button()
        button_zoom_out.set_icon_name('value-decrease-symbolic')
        button_zoom_out.set_has_frame(False)
        button_zoom_out.set_action_name('win.zoom-out')
        inner_box.append(button_zoom_out)

        self.reset_zoom_button = Gtk.Button.new_with_label('100%')
        self.reset_zoom_button.set_has_frame(False)
        self.reset_zoom_button.set_action_name('win.reset-zoom')
        self.reset_zoom_button.set_size_request(53, -1)
        inner_box.append(self.reset_zoom_button)

        button_zoom_in = Gtk.Button()
        button_zoom_in.set_icon_name('value-increase-symbolic')
        button_zoom_in.set_has_frame(False)
        button_zoom_in.set_action_name('win.zoom-in')
        inner_box.append(button_zoom_in)

        box.set_end_widget(inner_box)
        self.add_widget(box)
