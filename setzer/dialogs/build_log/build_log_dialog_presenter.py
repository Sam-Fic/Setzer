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


class BuildLogDialogPresenter(object):
    '''同步 build_log.items → dialog view，按设置项过滤显示哪些类型。

    `autoshow_build_log` 设置项的语义在 Pass-10 扩展为「弹窗显示哪些类型」：
      - 'errors'          → 仅 Errors
      - 'errors_warnings' → Errors + Warnings（不含 Badboxes）
      - 'all'             → Errors + Warnings + Badboxes

    该常量同时被 BuildLogDialogController.on_copy_all_clicked 引用，
    保证 Copy All 与显示范围一致。
    '''

    TYPE_FILTER = {
        'errors': {'Error'},
        'errors_warnings': {'Error', 'Warning'},
        'all': {'Error', 'Warning', 'Badbox'},
    }

    def __init__(self, build_log, dialog_view):
        self.build_log = build_log
        self.view = dialog_view

        # build_log 是 Observable；build_log_finished_adding 在 update_items 末尾触发。
        self.build_log.connect('build_log_finished_adding', self.on_build_log_finished_adding)

    def on_build_log_finished_adding(self, build_log, has_been_built):
        self.populate()

    def populate(self):
        '''重建弹窗内容：清空所有 group，按设置项过滤后重新追加 items。'''
        self.view.clear_all()

        autoshow = self.build_log.settings.get_value('preferences', 'autoshow_build_log')
        visible_types = self.TYPE_FILTER.get(autoshow, self.TYPE_FILTER['all'])

        any_visible = False
        for item in self.build_log.items:
            item_type = item[0]
            if item_type not in visible_types:
                continue
            # item 元组：item[0]=type, item[2]=filename, item[3]=line_number, item[4]=description
            self.view.add_item(item_type, item[2], item[3], item[4])
            any_visible = True

        # group 显隐：仅显示「在 visible_types 中 且 有内容」的 group。
        # 空 group 隐藏（含标题），避免「Warnings (0)」占位。
        for item_type, group in self.view.groups.items():
            has_content = self.view.lists[item_type].get_first_child() is not None
            group.set_visible(item_type in visible_types and has_content)

        # 全空时显示 empty_label
        self.view.empty_label.set_visible(not any_visible)

        # 滚动回顶：Adw.PreferencesPage 的第一个子是 ScrolledWindow（Pass-8 已验证）。
        scrolled = self.view.page.get_first_child()
        if scrolled is not None:
            scrolled.get_vadjustment().set_value(0)
            scrolled.get_hadjustment().set_value(0)

        # 更新 HeaderBar 标题为构建状态（原 BuildLogPresenter.set_header_data 的信息迁移至此）。
        self._update_header_title(has_been_built_implicit=True)

    def _update_header_title(self, has_been_built_implicit):
        '''根据构建结果更新 HeaderBar 副标题。

        原底部面板顶部显示「Building successful (1.23s, no warnings or badboxes).」
        等状态文本；弹窗化后改为 HeaderBar title=「Build Log」+ subtitle=状态文本。
        '''
        document = self.build_log.document
        if document is None or document.build_system is None:
            self.view.set_header_title(_('Build Log'), '')
            return

        build_system = document.build_system
        if not getattr(build_system, 'document_has_been_built', False):
            self.view.set_header_title(_('Build Log'), '')
            return

        num_errors = self.build_log.count_items('errors')
        num_others = self.build_log.count_items('warnings') + self.build_log.count_items('badboxes')

        # 时间字符串
        if build_system.build_time is not None:
            time_string = '{:.2f}s'.format(build_system.build_time)
        else:
            time_string = ''

        # 状态文本（与原 BuildLogPresenter.set_header_data 保持一致）
        if num_errors == 0:
            status = _('Building successful')
        else:
            status = ngettext('Building failed with {amount} error',
                              'Building failed with {amount} errors',
                              num_errors).format(amount=str(num_errors))

        if num_others == 0:
            warnings_text = _('no warnings or badboxes')
        else:
            warnings_text = ngettext('{amount} warning or badbox',
                                     '{amount} warnings or badboxes',
                                     num_others).format(amount=str(num_others))

        subtitle_parts = []
        if time_string:
            subtitle_parts.append(time_string)
        subtitle_parts.append(status)
        subtitle_parts.append(warnings_text)
        subtitle = ' · '.join(subtitle_parts) if subtitle_parts else ''

        self.view.set_header_title(_('Build Log'), subtitle)
