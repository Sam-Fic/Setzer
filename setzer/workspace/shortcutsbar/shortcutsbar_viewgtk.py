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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

from setzer.app.service_locator import ServiceLocator
from setzer.popovers.popover_manager import PopoverManager
from setzer.popovers.shortcutsbar.document_menu import DocumentMenu
from setzer.popovers.shortcutsbar.beamer_menu import BeamerMenu
from setzer.popovers.shortcutsbar.bibliography_menu import BibliographyMenu
from setzer.popovers.shortcutsbar.text_menu import TextMenu
from setzer.popovers.shortcutsbar.quotes_menu import QuotesMenu
from setzer.popovers.shortcutsbar.math_menu import MathMenu
from setzer.popovers.shortcutsbar.object_menu import ObjectMenu


class _NoNaturalWidthLayout(Gtk.BoxLayout):
    '''Gtk.BoxLayout subclass that reports natural width 0 horizontally.

    必要原因：preview_paned 的分隔条位置按子部件自然宽度自动分配。若
    shortcutsbar 自然宽度 = left_box 按钮数之和，则 reflow 把按钮移到 overflow
    时自然宽度变小 → paned 给编辑器列更少空间 → sb_width 变小 → reflow 算出
    更大 target → 移走更多按钮 → 自然宽度更小 …… 正反馈级联，target 在两个值
    之间震荡不收敛，按钮被裁切或反复跳动。

    返回 0 后：编辑器列宽度由 document_stack（源码编辑器）的自然宽度驱动，
    不随按钮数变化；shortcutsbar 通过 hexpand 的 _spacer 填充实际分配宽度，
    reflow 按该实际宽度收起按钮。feedback loop 断开。

    实现注意：GTK4 中 Gtk.Box 的 measure 由 layout manager 处理，覆写 widget
    的 do_measure 不生效（PyGObject 3.56.2 + GTK 4.22 验证：Gtk.Box 子类的
    do_measure 从未被调用）。必须覆写 Gtk.BoxLayout.do_measure 才能改变
    Gtk.Box 的测量结果。'''

    def do_measure(self, widget, orientation, for_size):
        if orientation == Gtk.Orientation.HORIZONTAL:
            # 横向返回 (0, 0)：min=0, nat=0，让 shortcutsbar 不参与父级宽度分配
            return (0, 0, -1, -1)
        else:
            # 纵向用默认测量（按内容决定高度）
            return Gtk.BoxLayout.do_measure(self, widget, orientation, for_size)


class Shortcutsbar(Gtk.Box):
    '''Icon bar above the editor. Uses libadwaita-style overflow menu
    (GNOME Builder/Text Editor pattern) instead of fixed-width wrapping:
    when the window is narrow, the rightmost left-side buttons are hidden
    from the bar and added to a `view-more-symbolic` popover instead.
    Public method `set_overflow_count(n)` moves the rightmost n left
    buttons into the popover; n=0 shows them all inline.

    `do_size_allocate` is overridden to **continuously** reflow based on
    the actual allocated width (instead of discrete Adw.Breakpoints that
    would only flip at fixed thresholds). The number of overflowed buttons
    matches the available space on every layout pass.'''

    def __init__(self):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_can_focus(False)
        # 关键：用自定义 layout manager 让横向自然宽度 = 0，断开 reflow 反馈环
        # （详见 _NoNaturalWidthLayout 文档）。必须在添加子部件之前设置。
        self.set_layout_manager(_NoNaturalWidthLayout())
        # 容器留白，强化"悬浮一排按钮"的视觉归属（无底板横条）
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self._margin_horizontal = 6
        self.set_margin_start(self._margin_horizontal)
        self.set_margin_end(self._margin_horizontal)

        self.current_popover = None # popover being processed
        self.current_page = 'main' # page being processed

        # 可见 left 按钮容器（普通 Gtk.Box，不是 FlowBox——避免 FlowBox
        # 内部布局对 children 拉伸/换行的副作用）。收起时从 left_box
        # remove 并加入 overflow menu model。
        self.left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.left_box.set_spacing(6)
        self.left_box.set_can_focus(False)

        # 右侧 4 个固定按钮容器
        self.right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.right_box.set_spacing(6)
        self.right_box.set_can_focus(False)

        # 中间弹簧：把 right_box 推到最右端（overflow 在 spacer 左侧，紧跟 left_box）
        self._spacer = Gtk.Box()
        self._spacer.set_hexpand(True)

        # Overflow button (三点) + popover (native Gtk.PopoverMenu via Gio.Menu)
        # 位置：紧跟 left_box（左半边按钮组的最右端）——因为收起的是左侧按钮，
        # 三点按钮应出现在左侧按钮群的末尾，而非整条工具栏的最右。
        self.overflow_button = Gtk.MenuButton()
        self.overflow_button.set_icon_name('view-more-symbolic')
        self.overflow_button.set_tooltip_text(_('More'))
        self.overflow_button.set_visible(False)  # 宽时隐藏
        self.overflow_button.set_margin_start(6)

        self._overflow_model = Gio.Menu()
        self.overflow_button.set_menu_model(self._overflow_model)
        overflow_popover = self.overflow_button.get_popover()
        if overflow_popover is not None:
            overflow_popover.add_css_class('menu')

        # 按钮元信息：icon_name, tooltip, menu_model (仅 MenuButton 有)
        self._button_meta = {}

        # 组装：left | overflow | spacer(hexpand) | right
        # overflow 紧跟 left_box；spacer 把 right_box 推到最右端。
        self.append(self.left_box)
        self.append(self.overflow_button)
        self.append(self._spacer)
        self.append(self.right_box)

        # 创建所有 left button（10 个，顺序：先建 = 最左，后建 = 最右）
        # self.left_buttons[0] = 最左, self.left_buttons[-1] = 最右
        self.left_buttons = []
        self.insert_wizard_button()        # 0
        self.insert_document_button()      # 1
        self.insert_beamer_button()        # 2
        self.insert_bibliography_button()  # 3
        self.insert_object_button()        # 4
        self.insert_text_button()          # 5
        self.insert_math_button()          # 6
        self.insert_quotes_button()        # 7
        self.insert_bold_button()          # 8
        self.insert_italic_button()        # 9 (最右)

        # 创建所有 right button（4 个）
        self.insert_search_button()
        self.insert_replace_button()
        self.insert_more_button()  # F12 context menu
        self.insert_build_log_button()

        # Overflow state: 0 = 全部 visible
        self._overflow_count = 0
        self._reflow_pending = False
        self._last_allocated_width = -1

    # ------- continuous reflow: 父级 size 变化时自动计算 overflow -------

    def do_size_allocate(self, width, height, baseline):
        Gtk.Box.do_size_allocate(self, width, height, baseline)
        # 异步 reflow 避免在 size-allocate 流程中改 widget tree
        if width != self._last_allocated_width and not self._reflow_pending:
            self._reflow_pending = True
            GLib.idle_add(self._reflow_idle, width)

    def _reflow_idle(self, available_width):
        self._reflow_pending = False
        self.reflow_for_width(available_width)
        self._last_allocated_width = available_width
        return False  # remove idle

    def request_reflow(self):
        '''Re-run reflow with the current allocated width.

        正常 reflow 只在 shortcutsbar 分配宽度变化时触发（do_size_allocate）。
        但按钮宽度可能因内容变化而改变，且不会引起 shortcutsbar 分配宽度变化
        （_NoNaturalWidthLayout 横向返回 0，paned 不会因此重分配）。这类情况包括：
          - wizard 按钮的 revealer 展开/收起（显示/隐藏 "New Document Wizard" 标签）
          - update_buttons 切换 latex 专属按钮的可见性
        此时需主动触发一次 reflow，按新的按钮宽度重新计算 overflow 数量。
        用 idle 延迟，确保 GTK 已处理 set_visible/set_reveal_child 后的新首选宽度。'''
        width = self.get_allocated_width()
        if width > 1:
            GLib.idle_add(self.reflow_for_width, width)

    def reflow_for_width(self, available_width):
        '''Compute how many left buttons fit in available_width and hide
        the rest into the overflow popover. Called by do_size_allocate
        (primary path) and the _poll_sb_width safety net.

        算法：测量每个 left button 的自然宽，累加得 left_total。测量 right 4 按钮
        和 overflow 按钮的自然宽。avail = available_width - right_total - margins
        - (overflow 按钮宽 + spacing 若 overflow visible)。
        若 left_total <= avail：target=0；否则按从右到左逐个收起，直到能塞下。
        为避免 feedback loop（reflow 改 tree→新 layout→新 reflow），overflow 按钮的
        宽度始终按"已显示"计算（即一旦 target>0 就一直预留 overflow 按钮空间）。'''
        if available_width <= 1:
            return
        # 只测量可见按钮：不可见按钮（如非 latex 文档时的 latex 专属按钮）
        # 不占布局空间，不计入宽度与数量，否则 left_total 虚高导致过度收起。
        #
        # 注意：必须用 measure()，不能用 get_preferred_width()——后者在较新
        # GTK4 已移除（AttributeError），若用 try/except 回退到 36 会让所有按钮
        # 都被测成 36px，对展开后约 160px 的 wizard 按钮失明，导致该收起时不收起。
        def _natural_width(widget):
            try:
                _min, nat, _b1, _b2 = widget.measure(Gtk.Orientation.HORIZONTAL, -1)
            except Exception:
                nat = 36
            return max(0, nat)

        left_widths = []
        for btn in self.left_buttons:
            if not btn.get_visible():
                continue
            left_widths.append(_natural_width(btn))
        right_widths = []
        for btn in [self.button_search, self.button_replace, self.button_more, self.button_build_log]:
            if not btn.get_visible():
                continue
            right_widths.append(_natural_width(btn))
        overflow_nat = _natural_width(self.overflow_button)

        spacing = 6
        n_left = len(left_widths)
        n_right = len(right_widths)

        left_total = sum(left_widths) + spacing * max(0, n_left - 1)
        right_total = sum(right_widths) + spacing * max(0, n_right - 1)
        # 始终预留 overflow 按钮空间（即使当前 target=0），避免 feedback loop
        # 当 target=0 时 overflow 按钮隐藏，下次 reflow 不会因它消失而扩张
        fixed = right_total + 2 * self._margin_horizontal + overflow_nat + spacing  # margins + overflow

        avail = available_width - fixed

        if left_total <= avail:
            target = 0
        else:
            excess = left_total - avail
            target = 0
            accumulated = 0
            for w in reversed(left_widths):
                accumulated += w + spacing
                target += 1
                if accumulated >= excess:
                    break
            target = min(target, n_left)

        target = max(0, target)
        if target != self._overflow_count:
            self.set_overflow_count(target)

    # ------- overflow API (called by MainWindow's Adw.Breakpoints) -------

    def set_overflow_count(self, n):
        '''Move the rightmost n left buttons into the overflow popover.
        0 = show all inline. Idempotent.'''
        n = max(0, min(n, len(self.left_buttons)))
        if n == self._overflow_count:
            return
        # 先把当前在 overflow 的所有 button 还原到 left_box
        for btn in self.left_buttons:
            if btn.get_parent() is not self.left_box:
                self.left_box.append(btn)
        # 把最后 n 个从 left_box 移除。
        # 注意：必须 guard n>0——Python 中 list[-0:] == list[0:]（整个列表），
        # 若不 guard，n=0 时会把刚还原的全部按钮又移除，导致最宽档位左侧按钮全消失。
        if n > 0:
            for btn in self.left_buttons[-n:]:
                self.left_box.remove(btn)
        # 重建 overflow menu model
        self._refresh_overflow_list(n)
        self._overflow_count = n
        # 0 时隐藏 overflow button，否则显示
        self.overflow_button.set_visible(n > 0)

    def _refresh_overflow_list(self, n):
        self._overflow_model.remove_all()
        if n == 0:
            return
        for btn in self.left_buttons[-n:]:
            meta = self._button_meta.get(id(btn))
            if meta is None:
                continue
            icon_name = meta['icon_name']
            tooltip = meta['tooltip']
            label = tooltip.split(' (', 1)[0]
            menu_model = meta.get('menu_model')
            if menu_model is not None:
                self._overflow_model.append_submenu(label, menu_model)
            else:
                item = Gio.MenuItem.new(label, meta.get('action_name'))
                target = meta.get('action_target')
                if target is not None:
                    item.set_action_and_target_value(meta['action_name'], target)
                if icon_name:
                    item.set_icon(Gio.ThemedIcon.new(icon_name))
                self._overflow_model.append_item(item)

    # ------- left button construction helpers -------

    def _add_left_button(self, button):
        '''Append a new left button to left_box and record it in left_buttons.'''
        self.left_box.append(button)
        self.left_buttons.append(button)

    def insert_wizard_button(self):
        self.wizard_button = Gtk.Button()
        self.wizard_button.set_icon_name('document-new-symbolic')
        self.wizard_button.set_tooltip_text(_('Create a template document'))
        self.wizard_button.set_can_focus(False)
        self.wizard_button.set_action_name('win.show-document-wizard')
        self._button_meta[id(self.wizard_button)] = {
            'icon_name': 'document-new-symbolic',
            'tooltip': _('Create a template document'),
            'menu_model': None,
            'action_name': 'win.show-document-wizard',
            'action_target': None,
        }

        self._add_left_button(self.wizard_button)

    def insert_document_button(self):
        self.document_button = Gtk.MenuButton()
        self.document_button.set_icon_name('application-x-addon-symbolic')
        self.document_button.set_tooltip_text(_('Document'))
        self._setup_menu_button(self.document_button, DocumentMenu())
        self._add_left_button(self.document_button)

    def insert_beamer_button(self):
        self.beamer_button = Gtk.MenuButton()
        self.beamer_button.set_icon_name('view-list-bullet-symbolic')
        self.beamer_button.set_tooltip_text(_('Beamer'))
        self._setup_menu_button(self.beamer_button, BeamerMenu())
        self._add_left_button(self.beamer_button)

    def insert_bibliography_button(self):
        self.bibliography_button = Gtk.MenuButton()
        self.bibliography_button.set_icon_name('library-symbolic')
        self.bibliography_button.set_tooltip_text(_('Bibliography'))
        self._setup_menu_button(self.bibliography_button, BibliographyMenu())
        self._add_left_button(self.bibliography_button)

    def insert_text_button(self):
        self.text_button = Gtk.MenuButton()
        self.text_button.set_icon_name('text-symbolic')
        self.text_button.set_tooltip_text(_('Text'))
        self._setup_menu_button(self.text_button, TextMenu())
        self._add_left_button(self.text_button)

    def insert_quotes_button(self):
        self.quotes_button = Gtk.MenuButton()
        self.quotes_button.set_icon_name('own-quotes-symbolic')
        self.quotes_button.set_tooltip_text(_('Quotes') + ' (' + _('Ctrl') + '+")')
        self._setup_menu_button(self.quotes_button, QuotesMenu())
        self._add_left_button(self.quotes_button)

    def insert_math_button(self):
        self.math_button = Gtk.MenuButton()
        self.math_button.set_icon_name('own-math-menu-symbolic')
        self.math_button.set_tooltip_text(_('Math'))
        self._setup_menu_button(self.math_button, MathMenu())
        self._add_left_button(self.math_button)

    def insert_object_button(self):
        self.insert_object_button = Gtk.MenuButton()
        self.insert_object_button.set_icon_name('insert-object-symbolic')
        self.insert_object_button.set_tooltip_text(_('Objects'))
        self._setup_menu_button(self.insert_object_button, ObjectMenu())
        self._add_left_button(self.insert_object_button)

    def insert_bold_button(self):
        self.bold_button = Gtk.Button()
        self.bold_button.set_icon_name('format-text-bold-symbolic')
        self.bold_button.set_action_name('win.insert-before-after')
        self.bold_button.set_action_target_value(GLib.Variant('as', ['\\textbf{', '}']))
        self.bold_button.set_tooltip_text(_('Bold') + ' (' + _('Ctrl') + '+B)')
        self._button_meta[id(self.bold_button)] = {
            'icon_name': 'format-text-bold-symbolic',
            'tooltip': _('Bold') + ' (' + _('Ctrl') + '+B)',
            'menu_model': None,
            'action_name': 'win.insert-before-after',
            'action_target': GLib.Variant('as', ['\\textbf{', '}']),
        }
        self._add_left_button(self.bold_button)

    def insert_italic_button(self):
        self.italic_button = Gtk.Button()
        self.italic_button.set_icon_name('format-text-italic-symbolic')
        self.italic_button.set_action_name('win.insert-before-after')
        self.italic_button.set_action_target_value(GLib.Variant('as', ['\\textit{', '}']))
        self.italic_button.set_tooltip_text(_('Italic') + ' (' + _('Ctrl') + '+I)')
        self._button_meta[id(self.italic_button)] = {
            'icon_name': 'format-text-italic-symbolic',
            'tooltip': _('Italic') + ' (' + _('Ctrl') + '+I)',
            'menu_model': None,
            'action_name': 'win.insert-before-after',
            'action_target': GLib.Variant('as', ['\\textit{', '}']),
        }
        self._add_left_button(self.italic_button)

    # ------- right button construction helpers -------

    def _add_right_button(self, button):
        self.right_box.append(button)

    def insert_search_button(self):
        self.button_search = Gtk.ToggleButton()
        self.button_search.set_icon_name('edit-find-symbolic')
        self.button_search.set_tooltip_text(_('Find') + ' (' + _('Ctrl') + '+F)')
        self._add_right_button(self.button_search)

    def insert_replace_button(self):
        self.button_replace = Gtk.ToggleButton()
        self.button_replace.set_icon_name('edit-find-replace-symbolic')
        self.button_replace.set_tooltip_text(_('Find and Replace') + ' (' + _('Ctrl') + '+H)')
        self._add_right_button(self.button_replace)

    def insert_more_button(self):
        self.button_more = Gtk.MenuButton()
        self.button_more.set_icon_name('view-more-symbolic')
        self.button_more.set_popover(PopoverManager.create_popover('context_menu').view)
        self.button_more.set_tooltip_text(_('Context Menu') + ' (F12)')
        self._add_right_button(self.button_more)

    def insert_build_log_button(self):
        self.button_build_log = Gtk.ToggleButton()
        self.button_build_log.set_icon_name('build-log-symbolic')
        self.button_build_log.set_tooltip_text(_('Build log') + ' (F8)')
        self._add_right_button(self.button_build_log)

    def _setup_menu_button(self, button, menu_builder):
        '''Wire a Gio.Menu model to a Gtk.MenuButton and add the standard
        .menu CSS class to the auto-created Gtk.PopoverMenu — identical to
        how the hamburger menu is set up.'''
        menu_builder.finalize()
        button.set_menu_model(menu_builder.model)
        popover = button.get_popover()
        if popover is not None:
            popover.add_css_class('menu')
        self._button_meta[id(button)] = {
            'icon_name': button.get_icon_name(),
            'tooltip': button.get_tooltip_text() or '',
            'menu_model': menu_builder.model,
        }


