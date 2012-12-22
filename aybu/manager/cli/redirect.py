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


class RedirectInterface(BaseInterface):

    commands = ['list', 'create', 'edit', 'info', 'delete']
    name = 'redirects'

    @plac.annotations(
        source=('Source domain to redirect', 'positional', None, str, None,
                'SOURCE_DOMAIN'),
        destination=('Destination instance', 'positional', None, str, None,
                     'DESTINATION_DOMAIN'),
        http_code=('HTTP code to issue', 'option', 'c'),
        target_path=('target path on the destination domain', 'option', 'p')
    )
    def create(self, source, destination, http_code=None, target_path=None):
        """ Create a new empty redirect """
        params = {'source': source,
                  'destination': destination}
        if http_code:
            params['http_code'] = http_code
        if target_path:
            params['target_path'] = target_path

        self.api.execute_sync_task('post', self.root_url, data=params)

    @plac.annotations(
        source=('Source domain to redirect', 'positional', None, str, None,
                'SOURCE_DOMAIN'),
        destination=('Destination instance', 'option', 'd', str, None,
                     'DESTINATION_DOMAIN'),
        http_code=('HTTP code to issue', 'option', 'c'),
        target_path=('target path on the destination domain', 'option', 'p')
    )
    def edit(self, source, destination=None, http_code=None, target_path=None):
        params = {}
        if destination:
            params['destination'] = destination
        if http_code:
            params['http_code'] = http_code
        if not target_path is None:
            params['target_path'] = target_path

        self.api.execute_sync_task('put', self.get_url(source), data=params)

    @plac.annotations(
        source=('The redirect to delete', 'positional')
    )
    def delete(self, source):
        """ Delete the selected resource """
        self.api.execute_sync_task('delete', self.get_url(source))

    @plac.annotations(
        full=('Get complete output', 'flag', 'f'),
        verbose=('Be verbose', 'flag', 'v')
    )
    def list(self, full=False, verbose=False):
        quiet = not verbose
        response, content = self.api.get(self.root_url, quiet=quiet)
        content = content or {}

        if not full:
            for source, data in content.iteritems():
                print " • {source} => {destination}{target_path} [{http_code}]"\
                        .format(**data)
        else:
            for source, data in content.iteritems():
                print " • {}:".format(source)
                self.print_info(data, prompt='   ° ')
