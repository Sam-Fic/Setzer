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


def WelcomeScreenView():
    '''Welcome screen shown when no document is open.

    Returns a configured Adw.StatusPage (icon + title + description).
    Adw.StatusPage 是 final 类型，无法被子类化，故以工厂函数返回实例，
    替代原来的手绘 Gtk.Box + Gtk.Label 居中布局。'''
    page = Adw.StatusPage()
    page.set_icon_name('text-x-tex-symbolic')
    page.set_title(_('Write beautiful LaTeX documents with ease!'))
    page.set_description(_('Click the open or create buttons in the headerbar above to start editing.'))
    return page
