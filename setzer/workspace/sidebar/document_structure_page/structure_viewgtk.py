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

import os.path

import setzer.workspace.sidebar.document_structure_page.structure_widget as structure_widget


class StructureSectionView(structure_widget.StructureWidget):

    def __init__(self, model):
        structure_widget.StructureWidget.__init__(self, model)

    def populate(self):
        self.clear_rows()
        self.add_nodes(self.model.nodes, 0)

    def add_nodes(self, nodes, level):
        for node in nodes:
            item = node['item']
            icon_name = item[2]
            if icon_name == 'file-symbolic':
                text = os.path.basename(item[3])
            else:
                text = item[3]
            row = self.make_row(icon_name, text, level * 18)
            row.item_data = node
            self.append(row)
            self.add_nodes(node['children'], level + 1)
