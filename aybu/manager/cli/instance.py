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


class InstanceInterface(BaseInterface):

    commands = ['list', 'deploy', 'delete', 'enable', 'disable', 'flush',
                'reload']
    name = 'instances'

    def deploy(self, domain, environment, owner, technical_contact,
               theme='', default_language='it', disabled=0):
        data=dict(
            domain=domain,
            environment_name=environment,
            owner_email=owner,
            technical_contact_email=technical_contact,
            theme=theme,
            default_language=default_language,
            enabled='true' if not disabled else '')
        self.api.execute_sync_task('post', self.root_url, data=data)

    def enable(self, domain):
        self.api.put(self.get_url(domain),
                     {'action': 'enable'})

    def disable(self, domain):
        self.api.put(self.get_url(domain),
                     {'action': 'disable'})

    def flush(self, domain):
        self.api.put(self.get_url(domain),
                     {'action': 'flush'})

    def reload(self, domain):
        self.api.put(self.get_url(domain),
                     {'action': 'reload'})
