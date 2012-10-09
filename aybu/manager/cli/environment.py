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


class EnvironmentInterface(BaseInterface):
    commands = ['list', 'create', 'delete', 'rename', 'info', 'rewrite']
    name = 'envs'
    root_url = '/environments'

    @plac.annotations(
        name=('Environment name', 'positional'),
        virtualenv_name=('Virtualenv name to associate to this env.', 'option',
                   'e', str, None, 'VENV')
    )
    def create(self, name, virtualenv_name=None):
        data = dict(name=name)
        if virtualenv_name:
            data['virtualenv_name'] = virtualenv_name

        self.api.execute_sync_task('post', self.root_url, data=data)

    def rename(self, name, newname):
        self.api.put(self.get_url(name), {'name': newname})

    @plac.annotations(
        name=('Name of the environment to delete', 'positional')
    )
    def delete(self, name):
        """ Delete the selected instance """
        self.api.execute_sync_task('delete', self.get_url(name))

    @plac.annotations(
        name=('Name of the environment to rewrite', 'positional')
    )
    def rewrite(self, name):
        self.api.execute_sync_task('put', self.get_url(name),
                                   data={'action': 'rewrite'})
