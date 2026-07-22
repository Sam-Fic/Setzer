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

from setzer.popovers.helpers.adw_popover_menu import AdwPopoverMenu
from setzer.popovers.popover_manager import PopoverManager


class ContextMenu(object):
    '''Workspace right-click (secondary-button) context menu for documents.

    Built on AdwPopoverMenu (Gtk.Popover + Gtk.ListBox + Adw.ActionRow with
    the ``boxed-list`` style). Action items use add_item (the GAction
    auto-triggers on activation and the popover closes via row-activated).
    The LaTeX-only items (comment/sync/separator) are toggled as whole rows
    via set_visible. The zoom controls live in a non-activatable custom row.
    '''

    def __init__(self, workspace):
        self.workspace = workspace
        self.document = None

        # The shortcutsbar "more" popover (F12). Retained because actions.py
        # updates its reset_zoom_button label on zoom changes.
        self.popover_more = PopoverManager.create_popover('context_menu')

        # The right-click popover, parented to the active document's view.
        self.popover_pointer = AdwPopoverMenu()
        self.popover_pointer.set_size_request(300, -1)
        self.popover_pointer.set_has_arrow(False)
        self.popover_pointer.set_offset(150, 0)
        self.popover_pointer.set_can_focus(False)
        self.build_popover_pointer()

        self.workspace.connect('new_active_document', self.on_new_active_document)

    def on_new_active_document(self, workspace=None, parameter=None):
        self.document = self.workspace.active_document
        visible = self.document != None and self.document.is_latex_document()
        self.comment_button_pointer.set_visible(visible)
        self.sync_button_pointer.set_visible(visible)
        self.latex_buttons_separator_pointer.set_visible(visible)

    def build_popover_pointer(self):
        self.add_basic_buttons(self.popover_pointer)

        self.comment_button_pointer = self.add_action_button(self.popover_pointer, _('Toggle Comment'), 'win.toggle-comment', shortcut=_('Ctrl') + '+K')
        self.sync_button_pointer = self.add_action_button(self.popover_pointer, _('Show in Preview'), 'win.forward-sync')
        self.latex_buttons_separator_pointer = self.popover_pointer.add_separator()

        # Zoom row: label + zoom-out / reset / zoom-in. These trigger actions
        # but must not close the popover, so they live in a custom row.
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
        self.reset_zoom_button_pointer = Gtk.Button.new_with_label('100%')
        self.reset_zoom_button_pointer.set_has_frame(False)
        self.reset_zoom_button_pointer.set_action_name('win.reset-zoom')
        self.reset_zoom_button_pointer.set_size_request(53, -1)
        inner_box.append(self.reset_zoom_button_pointer)
        button_zoom_in = Gtk.Button()
        button_zoom_in.set_icon_name('value-increase-symbolic')
        button_zoom_in.set_has_frame(False)
        button_zoom_in.set_action_name('win.zoom-in')
        inner_box.append(button_zoom_in)
        box.set_end_widget(inner_box)
        self.popover_pointer.add_custom(box)

    def add_basic_buttons(self, popover):
        self.add_action_button(popover, _('Undo'), 'win.undo', shortcut=_('Ctrl') + '+Z')
        self.add_action_button(popover, _('Redo'), 'win.redo', shortcut=_('Shift') + '+' + _('Ctrl') + '+Z')
        popover.add_separator()
        self.add_action_button(popover, _('Cut'), 'win.cut', shortcut=_('Ctrl') + '+X')
        self.add_action_button(popover, _('Copy'), 'win.copy', shortcut=_('Ctrl') + '+C')
        self.add_action_button(popover, _('Paste'), 'win.paste', shortcut=_('Ctrl') + '+V')
        self.add_action_button(popover, _('Delete'), 'win.delete-selection')
        popover.add_separator()
        self.add_action_button(popover, _('Select All'), 'win.select-all', shortcut=_('Ctrl') + '+A')
        popover.add_separator()

    def add_action_button(self, popover, label, action_name, shortcut=None):
        return popover.add_item(label, action_name, shortcut=shortcut)

    def popup_at_cursor(self, x, y):
        if self.document == None: return

        self.popover_pointer.unparent()
        self.popover_pointer.set_parent(self.document.view)
        rect = Gdk.Rectangle()
        rect.x = x
        rect.y = y
        rect.width = 1
        rect.height = 1
        self.popover_pointer.set_pointing_to(rect)
        self.popover_pointer.popup()
