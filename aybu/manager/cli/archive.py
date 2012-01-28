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

import os
import plac
from . interface import BaseInterface


class ArchiveInterface(BaseInterface):

    commands = ['list', 'create', 'rename', 'download', 'delete']
    name = 'archives'

    @plac.annotations(
        domain=('Instance to archive', 'positional', None, str,
                None, 'DOMAIN'),
        name=('Archive name', 'option', 'n')
    )
    def create(self, domain, name=None):
        """ Archive an instance """
        params = dict(domain=domain)
        if name:
            params['name'] = name
        self.api.execute_sync_task('post', self.root_url, params)

    @plac.annotations(
        name=('Existing archive name', 'positional', None, str, None, 'NAME'),
        new_name=('New archive name', 'positional', None, str, None, 'NAME')
    )
    def rename(self, name, new_name):
        self.api.put(self.get_url(name), {'name': new_name})

    @plac.annotations(
        name=('Archive to download', 'positional', None, str, None, 'NAME'),
        destination=('Path where to save the archive', 'positional', None,
                     str, None, 'PATH')
    )
    def download(self, name, destination):
        response, content = self.api.get(self.get_url(name))
        if os.path.isdir(destination):
            destination = os.path.join(destination, name)
        destination = "{}.tar.gz".format(destination)

        with open(destination, 'w') as f:
            f.write(response.content)
