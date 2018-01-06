#!/usr/bin/env python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*-
#
# Copyright (C) 2017, Egor Panasenko
#
# This file is part of Yandex Player.
#
# Yandex Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Yandex Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Yandex Player.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Egor Panasenko <gaura.panasenko@gmail.com>

import sys, gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from py import main

if __name__ == "__main__":
	sys.exit(main())
