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


class AliasInterface(BaseInterface):

    commands = ['list', 'create', 'edit', 'info', 'delete']
    name = 'aliases'

    @plac.annotations(
        domain=('Alias domain', 'positional', None, str, None, 'DOMAIN'),
        destination=('Destination instance', 'positional', None, str, None,
                     'DESTINATION_DOMAIN')
    )
    def create(self, domain, destination):
        """ Create a new empty alias """
        params = {'domain': domain,
                  'destination': destination}
        self.api.execute_sync_task('post', self.root_url, data=params)

    @plac.annotations(
        domain=('Alias domain', 'positional', None, str, None, 'DOMAIN'),
        destination=('Destination instance', 'option', 'd', str, None,
                     'DESTINATION_DOMAIN'),
        new_domain=('New domain for alias', 'option', 'n', str, None,
                    'DOMAIN'),
    )
    def edit(self, domain, destination=None, new_domain=None):
        params = {}
        if destination:
            params['destination'] = destination
        if new_domain:
            params['new_domain'] = new_domain

        self.api.execute_sync_task('put', self.get_url(domain), data=params)

    @plac.annotations(
        domain=('The alias to delete', 'positional')
    )
    def delete(self, domain):
        """ Delete the selected redomain """
        self.api.execute_sync_task('delete', self.get_url(domain))

    @plac.annotations(
        full=('Get complete output', 'flag', 'f'),
        verbose=('Be verbose', 'flag', 'v')
    )
    def list(self, full=False, verbose=False):
        quiet = not verbose
        response, content = self.api.get(self.root_url, quiet=quiet)
        content = content or {}

        for domain, data in content.iteritems():
            print " • {domain} => {destination}".format(**data)
