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
from gi.repository import Adw, Gtk, GLib

import os

from setzer.app.service_locator import ServiceLocator

import setzer.workspace.headerbar.headerbar_viewgtk as headerbar_view
import setzer.workspace.shortcutsbar.shortcutsbar_viewgtk as shortcutsbar_view
import setzer.workspace.preview_panel.preview_panel_viewgtk as preview_panel_view
import setzer.workspace.help_panel.help_panel_viewgtk as help_panel_view
import setzer.workspace.sidebar.sidebar_viewgtk as sidebar_view
import setzer.workspace.welcome_screen.welcome_screen_viewgtk as welcome_screen_view


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
        # 用 NONE 而非 CROSSFADE：CROSSFADE 有约 200ms 淡入淡出动画，期间
        # 旧页面与新页面同时绘制，切换文档（尤其是「新建 latex」）时左侧编辑器
        # 会延迟出现，给人「更新不及时/卡顿」的感觉。NONE 立即切换，无视觉延迟。
        self.document_stack.set_transition_type(Gtk.StackTransitionType.NONE)
        # 不设 set_size_request(550)——shortcutsbar 的 overflow reflow 会让
        # 按钮在窄宽时自动收起，不再需要硬性最小宽度。这样窗口可以拖到更小。
        self.document_stack.set_vexpand(True)

        self.document_stack_wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.document_stack_wrapper.append(self.shortcutsbar)
        self.document_stack_wrapper.append(self.document_stack)

        # Pass-10: build_log 从底部嵌入式 Gtk.Paned 改为 Adw.Dialog 弹窗
        # （BuildLogDialog），不再常驻 widget tree。原 build_log_paned（纵向
        # Gtk.Paned，编辑器在上、build_log 在下）整体移除，preview_paned 直接
        # 以 document_stack_wrapper 为 start_child。build_log 实例由 workspace
        # 持有（workspace.py:80），按需 present/close。
        self.preview_panel = preview_panel_view.PreviewPanelView()

        self.help_panel = help_panel_view.HelpPanelView()

        self.sidebar = sidebar_view.Sidebar()

        self.preview_paned_overlay = Gtk.Overlay()
        self.preview_help_stack = Gtk.Stack()
        # 浮层 headerbar 覆盖右侧预览/帮助区域顶部，必须留出 46px 上边距，
        # 否则预览工具栏和帮助面板的 ActionBar 会被标题栏遮住。
        self.preview_help_stack.set_margin_top(46)
        self.preview_help_stack.add_named(self.preview_panel, 'preview')
        self.preview_help_stack.add_named(self.help_panel, 'help')

        # preview_paned: 横向 Gtk.Paned（预览/帮助在右 = end child），可拖动分隔条调整宽度。
        # Pass-10: start_child 从 build_log_paned 改为 document_stack_wrapper
        # （build_log_paned 已移除）。
        self.preview_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.preview_paned.set_wide_handle(True)
        self.preview_paned.set_start_child(self.document_stack_wrapper)
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

        # 浮层 headerbar 会覆盖右侧内容区顶部，给内容区整体留出 headerbar
        # 高度的上边距，避免编辑器/预览内容被标题栏遮住。
        # 初始使用 46px 作为兜底，随后由 do_size_allocate 根据 headerbar
        # 实际分配高度动态调整，避免写死高度。
        self.document_stack_wrapper.set_margin_top(46)
        self.preview_help_stack.set_margin_top(46)

        # 不用 Adw.ToolbarView：headerbar 作为 overlay 叠在内容上方，
        # 这样侧边栏可以从窗口顶部开始，覆盖标题栏区域。
        # 关键：把 headerbar 作为右侧内容区 (preview_paned_overlay) 的 overlay，
        # 而不是整个窗口的 overlay。这样 headerbar 只覆盖编辑器/预览区，
        # 左侧 sidebar 完全不受其影响，内容也能正常显示。
        self.headerbar.widget.set_valign(Gtk.Align.START)
        self.preview_paned_overlay.add_overlay(self.headerbar.widget)

        self.content_overlay = Gtk.Overlay()
        self.content_overlay.set_child(self.mode_stack)
        self.popoverlay.set_child(self.content_overlay)

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

        # shortcutsbar overflow reflow 安全网：Shortcutsbar.do_size_allocate
        # 是主触发路径（同步 reflow，零延迟）。这里每 250ms 轮询一次作为兜底，
        # 覆盖 do_size_allocate 可能漏掉的边缘情况。主路径可靠时此轮询不做实际工作。
        # 直接用 _last_allocated_width 判断，无需独立的 _last_sb_width 变量。
        def _poll_sb_width():
            width = self.shortcutsbar.get_allocated_width()
            if width > 1 and width != self.shortcutsbar._last_allocated_width:
                self.shortcutsbar.reflow_for_width(width)
                self.shortcutsbar._last_allocated_width = width
            return True
        GLib.timeout_add(250, _poll_sb_width)


    def do_size_allocate(self, width, height, baseline):
        Adw.ApplicationWindow.do_size_allocate(self, width, height, baseline)

        # 根据浮层 headerbar 的实际高度动态调整编辑器/预览区的上边距，
        # 保证内容不会被标题栏遮住，同时避免硬编码固定高度。
        if hasattr(self, 'headerbar') and hasattr(self, 'document_stack_wrapper') and hasattr(self, 'preview_help_stack'):
            headerbar_height = self.headerbar.widget.get_allocated_height()
            if headerbar_height > 0:
                if self.document_stack_wrapper.get_margin_top() != headerbar_height:
                    self.document_stack_wrapper.set_margin_top(headerbar_height)
                if self.preview_help_stack.get_margin_top() != headerbar_height:
                    self.preview_help_stack.set_margin_top(headerbar_height)


