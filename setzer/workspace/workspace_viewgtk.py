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
from gi.repository import Adw, Gtk, GObject

import setzer.workspace.build_log.build_log_viewgtk as build_log_view
import setzer.workspace.headerbar.headerbar_viewgtk as headerbar_view
import setzer.workspace.shortcutsbar.shortcutsbar_viewgtk as shortcutsbar_view
import setzer.workspace.preview_panel.preview_panel_viewgtk as preview_panel_view
import setzer.workspace.help_panel.help_panel_viewgtk as help_panel_view
import setzer.workspace.sidebar.sidebar_viewgtk as sidebar_view
import setzer.workspace.welcome_screen.welcome_screen_viewgtk as welcome_screen_view


class _WidthReportingPaned(Gtk.Paned):
    '''Gtk.Paned that emits "width-changed" after each size allocation.

    GTK4 移除了 widget 的 size-allocate 信号（改为 vfunc），无法用 connect
    监听分配变化。此处覆盖 do_size_allocate 并发射自定义信号，供 shortcutsbar
    等需要响应编辑器列宽度变化的组件使用。'''

    __gsignals__ = {
        'width-changed': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def do_size_allocate(self, width, height, baseline):
        Gtk.Paned.do_size_allocate(self, width, height, baseline)
        self.emit('width-changed')


class MainWindow(Adw.ApplicationWindow):

    def __init__(self, app):
        Adw.ApplicationWindow.__init__(self, application=app)

        self.app = app
        # 设置最小宽度：使用 breakpoint（窄窗口折叠侧边栏）时 Adw 要求窗口有
        # width-request，否则会告警。360 为 libadwaita 惯用的窄窗口下限。
        self.set_size_request(360, 550)

        self.popoverlay = Gtk.Overlay()
        self.set_content(self.popoverlay)

    def create_widgets(self):
        self.shortcutsbar = shortcutsbar_view.Shortcutsbar()

        self.document_stack = Gtk.Stack()
        self.document_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.document_stack.set_size_request(550, -1)
        self.document_stack.set_vexpand(True)

        self.document_stack_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.document_stack_wrapper.append(self.shortcutsbar)
        self.document_stack_wrapper.append(self.document_stack)

        self.build_log = build_log_view.BuildLogView()

        # build_log_paned: 纵向 Gtk.Paned（原生 GTK4，编辑器在上，构建日志在下）
        self.build_log_paned = _WidthReportingPaned(orientation=Gtk.Orientation.VERTICAL)
        self.build_log_paned.set_start_child(self.document_stack_wrapper)
        self.build_log_paned.set_end_child(self.build_log)
        self.build_log_paned.set_resize_start_child(True)
        self.build_log_paned.set_resize_end_child(False)
        self.build_log_paned.set_shrink_start_child(False)
        self.build_log_paned.set_shrink_end_child(True)

        self.preview_panel = preview_panel_view.PreviewPanelView()

        self.help_panel = help_panel_view.HelpPanelView()

        self.sidebar = sidebar_view.Sidebar()

        self.preview_paned_overlay = Gtk.Overlay()
        self.preview_help_stack = Gtk.Stack()
        self.preview_help_stack.add_named(self.preview_panel, 'preview')
        self.preview_help_stack.add_named(self.help_panel, 'help')

        # preview_paned: 横向 Gtk.Paned（预览/帮助在右 = end child），可拖动分隔条调整宽度
        self.preview_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.preview_paned.set_wide_handle(True)
        self.preview_paned.set_start_child(self.build_log_paned)
        self.preview_paned.set_end_child(self.preview_help_stack)
        self.preview_paned.set_shrink_end_child(False)
        self.preview_paned_overlay.set_child(self.preview_paned)

        # sidebar_split: Adw.OverlaySplitView —— 原生可折叠侧边栏。
        # 宽窗口：侧边栏内联（与内容并排，等价原 Gtk.Paned 行为）；
        # 窄窗口（<700px breakpoint）：侧边栏折叠为浮层抽屉。
        # sidebar 为 Sidebar(Gtk.Stack)，含 symbols / document_structure 两页，共享同一抽屉。
        self.sidebar_split = Adw.OverlaySplitView()
        self.sidebar_split.set_sidebar(self.sidebar)
        self.sidebar_split.set_content(self.preview_paned_overlay)
        self.sidebar_split.set_min_sidebar_width(252)
        self.sidebar_split.set_max_sidebar_width(600)
        self.sidebar_split.set_sidebar_width_fraction(0.21)

        self.welcome_screen = welcome_screen_view.WelcomeScreenView()

        self.mode_stack = Gtk.Stack()
        self.mode_stack.add_named(self.welcome_screen, 'welcome_screen')
        self.mode_stack.add_named(self.sidebar_split, 'documents')

        self.headerbar = headerbar_view.HeaderBar()

        self.toolbar_view = Adw.ToolbarView()
        self.toolbar_view.add_top_bar(self.headerbar.widget)
        self.toolbar_view.set_content(self.mode_stack)
        self.popoverlay.set_child(self.toolbar_view)

        # 窄窗口自动把侧边栏折叠为浮层抽屉（Adw.OverlaySplitView 的 collapsed 属性）
        sidebar_breakpoint = Adw.Breakpoint.new(
            Adw.BreakpointCondition.new_length(Adw.BreakpointConditionLengthType.MAX_WIDTH, 700, Adw.LengthUnit.PX))
        sidebar_breakpoint.add_setter(self.sidebar_split, 'collapsed', True)
        self.add_breakpoint(sidebar_breakpoint)

        self.css_provider_font_size = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider_font_size, Gtk.STYLE_PROVIDER_PRIORITY_USER)


