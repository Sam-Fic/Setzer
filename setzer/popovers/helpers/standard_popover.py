#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
# This program is free software: you can redistribute it and
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib


class StandardMenuPopover(Gtk.Popover):
    '''标准 Libadwaita 风格弹出菜单。

    内部用 Gtk.ListBox 存放菜单项，提供：
    - add_item: 普通 action 项（点击触发 GAction 并关闭弹窗）
    - add_submenu: 子菜单项（嵌套 Gtk.MenuButton 弹出二级 StandardMenuPopover）
    - add_separator: 标准 Gtk.Separator 分隔线
    - add_custom: 直接放入任意 widget（用于非列表型布局，如两列数学函数）
    键盘导航（上下方向键、Enter 激活、Esc 关闭）由 Gtk.ListBox / Gtk.Popover 内置支持。
    '''

    def __init__(self):
        Gtk.Popover.__init__(self)
        self.set_size_request(288, -1)
        self.root_popover = self

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.add_css_class('menu')
        self.listbox.set_activate_on_single_click(True)
        self.set_child(self.listbox)

        self.listbox.connect('row-activated', self.on_row_activated)
        self.connect('map', self.on_map)
        self.connect('closed', self.on_closed)

        # 记录每个普通 action 行，供 row-activated 触发
        self.action_rows = list()

    def on_map(self, popover):
        # 让 ListBox 获得焦点以启用方向键导航
        self.listbox.grab_focus()

    def on_closed(self, popover):
        # 子菜单各自独立，无需重置
        pass

    def on_row_activated(self, listbox, row):
        child = row.get_child()
        # 普通 action 行：child 是 Gtk.Button（已绑定 action）
        if isinstance(child, Gtk.Button) and not isinstance(child, Gtk.MenuButton):
            child.activate()
            self.popdown()
            if self.root_popover is not self:
                self.root_popover.popdown()

    def _make_action_row(self, title, icon_name=None, shortcut=None):
        button = Gtk.Button()
        button.set_has_frame(False)
        button.add_css_class('flat')
        button.set_hexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button.set_child(box)

        # 图标列（固定宽度，保持对齐）
        if icon_name not in (None, 'placeholder'):
            icon = Gtk.Image(icon_name=icon_name)
            icon.set_pixel_size(16)
            box.append(icon)
        else:
            spacer = Gtk.Box()
            spacer.set_size_request(16, 1)
            box.append(spacer)

        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        label.set_xalign(0)
        box.append(label)

        if shortcut is not None:
            sc = Gtk.Label(label=shortcut)
            sc.add_css_class('dim-label')
            sc.set_xalign(1)
            box.append(sc)

        row = Gtk.ListBoxRow()
        row.set_child(button)
        return row, button

    def _make_submenu_row(self, title):
        menubutton = Gtk.MenuButton()
        menubutton.set_has_frame(False)
        menubutton.add_css_class('flat')
        menubutton.set_hexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        menubutton.set_child(box)

        spacer = Gtk.Box()
        spacer.set_size_request(16, 1)
        box.append(spacer)

        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        label.set_xalign(0)
        box.append(label)

        arrow = Gtk.Image(icon_name='pan-end-symbolic')
        box.append(arrow)

        row = Gtk.ListBoxRow()
        row.set_child(menubutton)
        row.set_activatable(False)
        return row, menubutton

    def add_item(self, title, action_name=None, target=None, icon_name=None, shortcut=None):
        '''添加一个普通菜单项。点击触发 action_name（带 target）并关闭弹窗。'''
        row, button = self._make_action_row(title, icon_name, shortcut)
        if action_name is not None:
            button.set_action_name(action_name)
            if target is not None:
                button.set_action_target_value(target)
        self.listbox.append(row)
        return row

    def add_submenu(self, title, submenu_popover):
        '''添加一个子菜单项，点击展开嵌套的二级弹窗。'''
        row, menubutton = self._make_submenu_row(title)
        menubutton.set_popover(submenu_popover)
        self.listbox.append(row)
        return row

    def add_separator(self):
        '''添加一条标准分隔线。'''
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        row = Gtk.ListBoxRow()
        row.set_child(separator)
        row.set_activatable(False)
        row.set_selectable(False)
        self.listbox.append(row)
        return row

    def add_custom(self, widget):
        '''直接放入任意 widget（用于非列表型布局）。'''
        row = Gtk.ListBoxRow()
        row.set_child(widget)
        row.set_activatable(False)
        row.set_selectable(False)
        self.listbox.append(row)
        return row

    def add_header(self, title):
        '''子菜单顶部的返回/标题行（可选，用于视觉层级）。'''
        button = Gtk.Button()
        button.set_has_frame(False)
        button.add_css_class('flat')
        button.set_hexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button.set_child(box)

        back = Gtk.Image(icon_name='pan-start-symbolic')
        box.append(back)

        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        label.set_xalign(0)
        box.append(label)

        row = Gtk.ListBoxRow()
        row.set_child(button)
        self.listbox.append(row)
        return row


class StandardMenuViewBase(StandardMenuPopover):
    '''供具体菜单视图继承的基类。

    把原 Popover 框架的 add_page / add_menu_button / add_before_after_item /
    add_insert_symbol_item / add_action_button / add_widget / add_separator
    转发到对应的标准 StandardMenuPopover 实例（main 或嵌套子菜单）。
    具体视图只需把内容代码照搬，并把 __init__ 基类改为本类即可。
    '''

    def __init__(self):
        StandardMenuPopover.__init__(self)
        self.pages = {'main': self}

    def add_page(self, pagename, label=None):
        if pagename not in self.pages:
            page = StandardMenuPopover()
            page.root_popover = self.root_popover
            if label is not None:
                page.add_header(label)
            self.pages[pagename] = page
        return self.pages[pagename]

    def add_menu_button(self, title, menu_name):
        submenu = self.pages.get(menu_name)
        if submenu is None:
            submenu = self.add_page(menu_name, title)
        self.pages['main'].add_submenu(title, submenu)

    def add_before_after_item(self, pagename, title, commands, icon=None, shortcut=None):
        self.pages[pagename].add_item(title, 'win.insert-before-after',
                                      GLib.Variant('as', commands), icon, shortcut)

    def add_insert_symbol_item(self, pagename, title, command, icon=None, shortcut=None):
        self.pages[pagename].add_item(title, 'win.insert-symbol',
                                      GLib.Variant('as', command), icon, shortcut)

    def add_action_button(self, pagename, title, action_name, parameter=None, icon=None, shortcut=None):
        return self.pages[pagename].add_item(title, action_name, parameter, icon, shortcut)

    def add_widget(self, widget, pagename='main'):
        return self.pages[pagename].add_custom(widget)

    def add_separator(self, pagename='main'):
        # 'main' 页就是 self（见 __init__ 的 self.pages = {'main': self}），
        # 直接调父类 StandardMenuPopover.add_separator，否则会无限自递归。
        if pagename == 'main':
            return StandardMenuPopover.add_separator(self)
        return self.pages[pagename].add_separator()

    def set_width(self, width):
        self.set_size_request(width, -1)


