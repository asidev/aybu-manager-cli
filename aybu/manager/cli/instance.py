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


class InstanceInterface(BaseInterface):

    commands = ['list', 'deploy', 'delete', 'enable', 'disable', 'flush',
                'switch_env', 'reload', 'delete', 'archive', 'restore', 'info',
                'migrate']
    name = 'instances'

    @plac.annotations(
        domain=('Domain to deploy', 'positional', None),
        environment=('Env to deploy to', 'positional'),
        owner=('Owner of the instance', 'positional'),
        technical_contact=('Tech contact of the instance', 'option', 'c', str,
                          None, 'EMAIL'),
        theme=('Theme name', 'option', 't', str, None, 'THEME_NAME'),
        default_language=('Default language for autoredirect', 'option', 'l'),
        disabled=('Mark the instance as disabled once deployed', 'flag', 'd'),
        verbose=('Enable debugging messages', 'flag', 'v')
    )
    def deploy(self, domain, environment, owner, technical_contact=None,
               theme='', default_language='it', disabled=False, verbose=False):
        """ deploy a new instance for a given domain. """
        data = dict(
            domain=domain,
            environment_name=environment,
            owner_email=owner,
            theme_name=theme,
            default_language=default_language,
            verbose='true' if verbose else '',
            enabled='true' if not disabled else '')
        if technical_contact:
            data['technical_contact_email'] = technical_contact,
        self.api.execute_sync_task('post', self.root_url, data=data)

    @plac.annotations(domain=('The instance to enable', 'positional'))
    def enable(self, domain):
        """ Reenable a previously disabled instance """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   {'action': 'enable'})

    @plac.annotations(domain=('The instance to disable', 'positional'))
    def disable(self, domain):
        """ Disable an instance, i.e. it stops the vassal but keep data and db
            in place"""
        self.api.execute_sync_task('put', self.get_url(domain),
                                   {'action': 'disable'})

    @plac.annotations(domain=('The instance to flush', 'positional'))
    def flush(self, domain):
        """ Flush cache for an instance """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   {'action': 'flush_cache'})

    @plac.annotations(domain=('The instance to reload', 'positional'))
    def reload(self, domain):
        """ Reload the vassal for an instance """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   {'action': 'reload'})

    @plac.annotations(domain=('The instance to kill', 'positional'))
    def kill(self, domain):
        """ Kill an instance's vassal sending SIGTERM to the process """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   {'action': 'kill'})

    @plac.annotations(domain=('The instance to kill', 'positional'))
    def sentence(self, domain):
        """ Kill an instance's vassal sending a SIGKILL to the process """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   {'action': 'sentence'})

    @plac.annotations(domain=('The instance to archive', 'positional'))
    def archive(self, domain):
        """ Create an archive of an instance. """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   {'action': 'restore'})

    @plac.annotations(domain=('The instance to restore', 'positional'))
    def restore(self, domain, archive):
        """ Restore an instance using a pre-created archive """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   {'action': 'restore',
                                    'archive': archive})
    @plac.annotations(
        domain=('The instance to delete', 'positional'),
        disable=('Disable instance before deleting', 'flag', 'd'),
    )
    def delete(self, domain, disable=False):
        """ Delete the selected instance """
        if disable:
            self.disable(domain)
        self.api.execute_sync_task('delete', self.get_url(domain))

    @plac.annotations(
        domain=('The instance to modify', 'positional'),
        environment=('The new environment to switch to', 'positional')
    )
    def switch_env(self, domain, environment):
        self.api.execute_sync_task('put', self.get_url(domain),
                                   {'action': 'switch_environment',
                                    'environment': environment})

    @plac.annotations(
        domain=('The instance to migrate', 'positional'),
        revision=('Schema revision to migrate to', 'option', 'm', str, None,
                  'REV')
    )
    def migrate(self, domain, revision='head'):
        self.api.execute_sync_task('put', self.get_url(domain),
                                   {'action': 'migrate',
                                    'revision': revision})



