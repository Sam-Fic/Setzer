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
from gi.repository import Adw, Gtk, GObject, GLib

import os
import sys

from setzer.app.service_locator import ServiceLocator

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
    等需要响应编辑器列宽度变化的组件使用。

    注：PyGObject 对 Gtk.Paned.do_size_allocate 的 vfunc 覆写在某些 GTK4 版本
    不可靠。本类另用 Gtk.EventControllerScroll+Motion 不可行；改在 MainWindow
    上用 notify::default-width 信号驱动 shortcutsbar.reflow_for_width()。本类的
    width-changed 信号仍保留向后兼容（presenter 已 connect 它），但 reflow 主路径
    不依赖此信号。'''

    __gsignals__ = {
        'width-changed': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, **kwargs):
        Gtk.Paned.__init__(self, **kwargs)

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
        # 不设 set_size_request(550)——shortcutsbar 的 overflow reflow 会让
        # 按钮在窄宽时自动收起，不再需要硬性最小宽度。这样窗口可以拖到更小。
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
        # shrink_start_child=True 允许编辑器列被压缩，配合 shortcutsbar overflow
        # 让窗口可以拖到很窄
        self.build_log_paned.set_shrink_start_child(True)
        self.build_log_paned.set_shrink_end_child(True)
        # 不设 set_size_request(550)——shortcutsbar 的 overflow reflow 会让
        # 按钮在窄宽时自动收起，不再需要硬性最小宽度。这样窗口可以拖到更小。

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
        # shrink_start_child=True：编辑器列允许收缩到低于其自然宽度。
        # 必要原因：shortcutsbar 在最宽档位（target=0）时全部 10 个左侧按钮都在
        # left_box，自然宽度约 630px。若 shrink=False，编辑器列不能低于 630px，
        # 窗口拖不窄、shortcutsbar 宽度始终 ≥630px，reflow 永远算出 target=0，
        # 按钮永远不收起。设 True 后缩窄窗口 → shortcutsbar 跟着窄 → reflow 折叠。
        # shrink_end_child=False：预览栏维持自然宽度（PDF 页宽），由编辑器列弹性收缩。
        self.preview_paned.set_shrink_start_child(True)
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
        # 注意：shortcutsbar overflow 现在由 Shortcutsbar.do_size_allocate
        # 连续测量后动态计算（每像素自适应），不再用 Adw.Breakpoint 阶梯。


        self.css_provider_font_size = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(self.get_display(), self.css_provider_font_size, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # 加载项目自定义 CSS（仅 shortcutsbar 的 FlowBoxChild padding 归零等少量微调，
        # 见 data/resources/style_gtk.css）。FONT 优先级在 USER 之上，确保我们的
        # 微调规则不被 libadwaita 默认 flowbox 样式覆盖。
        css_file = os.path.join(ServiceLocator.get_resources_path(), 'style_gtk.css')
        if os.path.exists(css_file):
            self.css_provider_app = Gtk.CssProvider()
            self.css_provider_app.load_from_path(css_file)
            Gtk.StyleContext.add_provider_for_display(
                self.get_display(), self.css_provider_app,
                Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # shortcutsbar overflow reflow：GTK4 没有暴露 widget size-allocate 信号，
        # 用 GLib.timeout_add 周期性测量 shortcutsbar 自身实际宽度，宽度变化时
        # 触发 reflow_for_width()。每 200ms 检查一次，开销可忽略。
        # 关键：必须测 shortcutsbar 自身宽度（= build_log_paned 宽度，不含 sidebar
        # 和 preview），而不是窗口宽度。窗口 1536px 但 sidebar+preview 占大半时，
        # shortcutsbar 可能只有 500px——若传 1536 给 reflow，会误判有空间导致
        # target=0，按钮被挤出去。
        # 防抖：reflow 改 widget tree 会触发新的 size-allocate，宽度可能震荡；
        # 用 _reflow_source 防止叠加，且只在宽度稳定后 reflow。
        self._last_sb_width = -1
        self._reflow_source = None
        self._pending_width = None
        _dbg = os.environ.get('SETZER_DEBUG_OVERFLOW')
        def _poll_sb_width():
            width = self.shortcutsbar.get_allocated_width()
            if _dbg:
                print(f"[poll] sb_width={width} last={self._last_sb_width}", file=sys.stderr)
            if width > 1 and width != self._last_sb_width:
                self._pending_width = width
                # 延迟 50ms 再 reflow，让 GTK 完成布局重算
                if self._reflow_source is None:
                    self._reflow_source = GLib.timeout_add(50, _do_reflow)
            return True  # continue polling
        def _do_reflow():
            self._reflow_source = None
            if self._pending_width is None:
                return False
            width = self._pending_width
            self._pending_width = None
            if width != self._last_sb_width:
                self._last_sb_width = width
                if _dbg:
                    print(f"[reflow] -> reflow_for_width({width})", file=sys.stderr)
                self.shortcutsbar.reflow_for_width(width)
            return False
        GLib.timeout_add(200, _poll_sb_width)


