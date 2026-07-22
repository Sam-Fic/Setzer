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
from gi.repository import Gdk, Gtk

from setzer.popovers.helpers.standard_popover import StandardMenuPopover


class ContextMenu(object):
    '''Preview right-click (secondary-button) context menu.

    Migrated from MenuBuilder.create_menu() (PopoverMenu) to StandardMenuPopover.
    Each entry is a plain menu item (add_item, no action); row activation calls
    button.activate() (emitting 'clicked' for the presenter's callback) and then
    closes the popover. zoom_in/out store their rows so update_buttons can
    disable the whole row (insensitive rows are not activatable).
    '''

    def __init__(self, preview, preview_view):
        self.preview = preview
        self.preview_view = preview_view

        self.popup_offset_x, self.popup_offset_y = 0, 0

        self.popover_pointer = StandardMenuPopover()
        self.popover_pointer.set_position(Gtk.PositionType.BOTTOM)
        self.popover_pointer.set_parent(self.preview_view.content.content)
        self.popover_pointer.set_size_request(260, -1)
        self.popover_pointer.set_has_arrow(False)
        self.popover_pointer.set_offset(130, 0)
        self.popover_pointer.set_can_focus(False)
        self.build_popover(self.popover_pointer)

        self.update_buttons()

        self.preview.zoom_manager.connect('zoom_level_changed', self.on_zoom_level_changed)
        self.preview_view.content.connect('secondary_button_press', self.on_secondary_button_press)

    def on_zoom_level_changed(self, preview):
        self.update_buttons()

    def on_secondary_button_press(self, content, data):
        if self.preview.layout == None: return True

        x_offset, y_offset, state = data
        self.popup_offset_x, self.popup_offset_y = x_offset, y_offset
        self.popup_at_cursor(x_offset - content.scrolling_offset_x, y_offset - content.scrolling_offset_y)

        return True

    def build_popover(self, popover):
        self.add_callback_button(popover, _('Show Source'), self.show_source)
        popover.add_separator()
        self.button_zoom_in = self.add_callback_button(popover, _('Zoom In'), self.zoom_in)
        self.button_zoom_out = self.add_callback_button(popover, _('Zoom Out'), self.zoom_out)
        self.add_callback_button(popover, _('Fit to Width'), self.zoom_fit_to_width)
        self.add_callback_button(popover, _('Fit to Text Width'), self.zoom_fit_to_text_width)
        self.add_callback_button(popover, _('Fit to Height'), self.zoom_fit_to_height)

    def add_callback_button(self, popover, label, callback):
        row = popover.add_item(label)
        row.get_child().connect('clicked', callback)
        return row

    def popup_at_cursor(self, x, y):
        rect = Gdk.Rectangle()
        rect.x = x
        rect.y = y
        rect.width = 1
        rect.height = 1
        self.popover_pointer.set_pointing_to(rect)
        self.popover_pointer.popup()

    def show_source(self, button):
        self.preview.init_backward_sync(self.popup_offset_x, self.popup_offset_y)
        self.popover_pointer.popdown()

    def zoom_in(self, button):
        self.preview.zoom_manager.zoom_in()
        self.popover_pointer.popdown()

    def zoom_out(self, button):
        self.preview.zoom_manager.zoom_out()
        self.popover_pointer.popdown()

    def zoom_fit_to_width(self, button):
        self.preview.zoom_manager.set_zoom_fit_to_width_auto_offset()
        self.popover_pointer.popdown()

    def zoom_fit_to_text_width(self, button):
        self.preview.zoom_manager.set_zoom_fit_to_text_width()
        self.popover_pointer.popdown()

    def zoom_fit_to_height(self, button):
        self.preview.zoom_manager.set_zoom_fit_to_height()
        self.popover_pointer.popdown()

    def update_buttons(self):
        zoom_level = self.preview.zoom_manager.get_zoom_level()

        self.button_zoom_in.set_sensitive(zoom_level != None and zoom_level < 4)
        self.button_zoom_out.set_sensitive(zoom_level != None and zoom_level > 0.25)
