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

from setzer.app.service_locator import ServiceLocator


class WelcomeScreen(object):
    '''Welcome screen presenter.

    Formerly drove a Cairo rotating-text animation over a DrawingArea; the
    view is now a plain static Gtk.Box, so there is nothing to drive.
    activate()/deactivate() are retained as no-ops for call-site
    compatibility.
    '''

    def __init__(self):
        self.view = ServiceLocator.get_main_window().welcome_screen
        self.is_active = False
        self.activate()

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False
