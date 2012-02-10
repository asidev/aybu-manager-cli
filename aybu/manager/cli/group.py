#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

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
        instance=('Instance for the group', 'option', 'i', str, None, 'DOMAIN')
    )
    def create(self, group, instance=None):
        """ Create a new empty group """
        data = dict(name=group)
        if instance:
            data['instance'] = instance
        self.api.post(self.get_url(), data=data)

    @plac.annotations(
        name=('Existing group name', 'positional', None, str, None, 'NAME'),
        new_name=('New group name', 'option', 'n', str, None, 'NAME'),
        instance=('Instance for the group', 'option', 'i', str, None, 'DOMAIN')
    )
    def update(self, name, new_name=None, instance=None):
        params = dict()
        if new_name:
            params['name'] = new_name
        if not instance is None:
            params['instance'] = instance
        if not params:
            self.log.error("You need to pass either a new name or a instance!")
        else:
            self.api.put(self.get_url(name), data=params)
