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


class ColorManager():

    main_window = None

    # 自定义颜色名 -> 内置 Libadwaita/GTK 调色板同名回退（语义相近）
    fallback_colors = {
        'window_fg_color': 'window_fg_color',
        'window_bg_color': 'window_bg_color',
        'view_fg_color': 'view_fg_color',
        'view_bg_color': 'view_bg_color',
        'view_hover_color': 'view_hover_color',
        'borders': 'borders',
        'error_color': 'error_color',
        'link_color': 'link_color',
        'link_color_visited': 'visited_link_color',
        'link_color_active': 'link_color',
        'fg_color_light': 'window_fg_color',
        'popover_bg_color': 'popover_bg_color',
        'list_selection_color': 'accent_color',
        'list_selection_hover_color': 'accent_color',
        'ac_bg': 'view_bg_color',
        'ac_selection_bg': 'accent_color',
        'ac_text': 'view_fg_color',
        'highlight_tag_textview': 'accent_color',
        'highlight_tag_preview': 'accent_color',
        'line_highlighting_color': 'accent_color',
        'code_folding_hover': 'accent_color',
    }

    def init(main_window):
        ColorManager.main_window = main_window

    def get_ui_color(name):
        style_context = ColorManager.main_window.get_style_context()
        found, rgba = style_context.lookup_color(name)
        if found:
            return rgba
        # 回退到 GTK/Libadwaita 内置调色板同名色
        fallback = ColorManager.fallback_colors.get(name, name)
        found, rgba = style_context.lookup_color(fallback)
        if found:
            return rgba
        # 最后兜底：不透明黑色，避免崩溃
        return Gdk.RGBA(0, 0, 0, 1)

    def get_ui_color_string(name):
        color_rgba = ColorManager.get_ui_color(name)
        color_string = '#'
        color_string += format(int(color_rgba.red * 255), '02x')
        color_string += format(int(color_rgba.green * 255), '02x')
        color_string += format(int(color_rgba.blue * 255), '02x')
        return color_string

    def get_ui_color_string_with_alpha(name):
        color_rgba = ColorManager.get_ui_color(name)
        color_string = '#'
        color_string += format(int(color_rgba.red * 255), '02x')
        color_string += format(int(color_rgba.green * 255), '02x')
        color_string += format(int(color_rgba.blue * 255), '02x')
        color_string += format(int(color_rgba.alpha * 255), '02x')
        return color_string


