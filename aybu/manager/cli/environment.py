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

from . interface import BaseInterface


class EnvironmentInterface(BaseInterface):
    commands = ['list', 'create', 'delete', 'rename']
    name = 'envs'
    root_url = '/environments'

    def create(self, name, venv_name=None):
        data = dict(name=name)
        if venv_name:
            data['venv_name'] = venv_name

        self.api.execute_sync_task('post', self.root_url, data=data)

    def rename(self, name, newname):
        self.api.put(self.get_url(name), {'name': newname})
