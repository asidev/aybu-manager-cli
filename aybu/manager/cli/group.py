#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 Asidev s.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import plac
from . interface import BaseInterface


class GroupInterface(BaseInterface):
    commands = ['list', 'create', 'update', 'info', 'delete']
    name = 'groups'

    @plac.annotations(
        group=('Group name', 'positional', None, str, None, 'NAME'),
        parent=('Parent group name (must exists)', 'option', 'p')
    )
    def create(self, group, parent=None):
        """ Create a new empty group """
        data = dict(name=group)
        if parent:
            data['parent'] = parent

        self.api.post(self.get_url(), data=data)

    @plac.annotations(
        name=('Existing group name', 'positional', None, str, None, 'NAME'),
        new_name=('New group name', 'option', 'n', str, None, 'NAME'),
        parent=('Parent group name (must exists)', 'option', 'p')
    )
    def update(self, name, new_name=None, parent=None):
        params = dict()
        if new_name:
            params['name'] = new_name

        if not parent is None:
            params['parent'] = parent

        if not params:
            self.log.error("No new params to update!")

        else:
            self.api.put(self.get_url(name), data=params)
