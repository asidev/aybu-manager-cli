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
from . archive import ArchiveInterface


class InstanceInterface(BaseInterface):

    commands = ['list', 'deploy', 'delete', 'enable', 'disable', 'flush',
                'switch_env', 'reload', 'reload_all', 'rewrite', 'rewrite_all',
                'delete', 'archive', 'restore', 'info', 'migrate', 'kill',
                'force_reload', 'change_domain', 'groups_add', 'groups_remove',
                'groups_empty', 'groups_set', 'allowed_users', 'migrate_all']
    name = 'instances'

    @plac.annotations(
        full=('Get complete output', 'flag', 'f'),
        verbose=('Be verbose', 'flag', 'v')
    )
    def list(self, full=False, verbose=False, **attributes):
        """ List instances. Add every search query at the end, using
            field=value.
            i.e. instances_list onwer_email=user@example.com sort_by=domain
        """
        quiet = not verbose
        response, content = self.api.get(self.root_url, quiet=quiet,
                                         query_params=attributes)

        if not full and content:
            self.log.info("environment  disabled  domain")
            self.log.info("-----------  --------  %s", "-" * 32)

        content = content or {}
        keys = sorted(content) if not 'sort_by' in attributes else content

        for res in keys:
            marker = ''
            if content[res]['enabled'] == False:
                marker = 'x'

            if full:
                self.log.info(" • {}".format(res))
                self.print_info(content[res], prompt='   ° ')

            else:
                self.log.info("{1:^11}  {2:^8}  {0}"\
                        .format(res, content[res]['environment_name'], marker))

    @plac.annotations(
        domain=('Domain to deploy', 'positional', None),
        environment=('Env to deploy to', 'positional'),
        owner=('Owner of the instance', 'positional'),
        technical_contact=('Tech contact of the instance', 'option', 'c', str,
                          None, 'EMAIL'),
        theme=('Theme name', 'option', 't', str, None, 'THEME_NAME'),
        default_language=('Default language for autoredirect', 'option', 'l'),
        disabled=('Mark the instance as disabled once deployed', 'flag', 'd'),
        verbose=('Enable debugging messages', 'flag', 'v'),
        groups=('Additional groups to add to instance (comma separated)',
                'option', 'G')
    )
    def deploy(self, domain, environment, owner, technical_contact=None,
               theme='', default_language='it', disabled=False, verbose=False,
               groups=None):
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
        if groups:
            # this will fail if task fail or it is deferred
            self.groups_set(domain, *groups.split(","))

    @plac.annotations(domain=('The instance to enable', 'positional'))
    def enable(self, domain):
        """ Reenable a previously disabled instance """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   data={'action': 'enable'})

    @plac.annotations(domain=('The instance to disable', 'positional'))
    def disable(self, domain):
        """ Disable an instance, i.e. it stops the vassal but keep data and db
            in place"""
        self.api.execute_sync_task('put', self.get_url(domain),
                                   data={'action': 'disable'})

    @plac.annotations(domain=('The instance to flush', 'positional'))
    def flush(self, domain):
        """ Flush cache for an instance """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   data={'action': 'flush_cache'})

    @plac.annotations(domain=('The instance to reload', 'positional'))
    def reload(self, domain):
        """ Reload the vassal for an instance """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   data={'action': 'reload'})

    def reload_all(self):
        """ Reload all instances at once"""
        self.api.execute_sync_task('put', self.root_url,
                                   data={'action': 'reload'})

    @plac.annotations(domain=('The instance to rewrite', 'positional'))
    def rewrite(self, domain):
        """ Rewrite instance config (thus reloading the uwsgi vassal) """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   data={'action': 'rewrite'})

    def rewrite_all(self):
        """ Rewrite all instances at once"""
        self.api.execute_sync_task('put', self.root_url,
                                   data={'action': 'rewrite'})

    @plac.annotations(
        domain=('The instance to kill', 'positional'),
    )
    def force_reload(self, domain):
        """ Kill an instance's vassal sending SIGTERM to the process """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   data={'action': 'reload',
                                         'force': 'true'})

    @plac.annotations(domain=('The instance to kill', 'positional'))
    def kill(self, domain):
        """ Kill an instance's vassal sending a SIGKILL to the process """
        self.api.execute_sync_task('put', self.get_url(domain),
                                   data={'action': 'reload',
                                         'kill': 'true'})

    @plac.annotations(
        domain=('The instance to archive', 'positional'),
        name=('Archive name', 'option', 'n')
    )
    def archive(self, domain, name=None):
        """ Create an archive of an instance. """
        archives_url = "/{}".format(ArchiveInterface.name)
        params = dict(domain=domain)
        if name:
            params['name'] = name
        self.api.execute_sync_task('post', archives_url, data=params)

    @plac.annotations(
        domain=('The instance to restore', 'positional'),
        archive_file=('Archive from file', 'option', 'f', str, None, 'FILE'),
        archive=('Archive name', 'option', 'n', str, None, 'NAME')
    )
    def restore(self, domain, archive_file=None, archive=None):
        """ Restore an instance using a pre-created archive """
        params = dict(action='restore')
        # TODO handle archive upload
        if archive:
            params['archive'] = archive
        self.api.execute_sync_task('put', self.get_url(domain), data=params)

    @plac.annotations(
        domain=('The instance to rename', 'positional'),
        new_domain=('New instance domain', 'positional')
    )
    def change_domain(self, domain, new_domain):
        """ Restore an instance using a pre-created archive """
        params = dict(action='change_domain', domain=new_domain)
        self.api.execute_sync_task('put', self.get_url(domain), data=params)

    @plac.annotations(
        domain=('The instance to delete', 'positional'),
        disable=('Disable instance before deleting', 'flag', 'd'),
        noarchive=('Do not archive before deleting', 'flag', 'n')
    )
    def delete(self, domain, disable=False, noarchive=False):
        """ Delete the selected instance """
        if disable:
            self.disable(domain)
        params = {'archive': 'true' if not noarchive else ''}
        self.api.execute_sync_task('delete', self.get_url(domain),
                                   data=params)

    @plac.annotations(
        domain=('The instance to modify', 'positional'),
        environment=('The new environment to switch to', 'positional')
    )
    def switch_env(self, domain, environment):
        self.api.execute_sync_task('put', self.get_url(domain),
                                   data={'action': 'switch_environment',
                                         'environment': environment})

    @plac.annotations(
        domain=('The instance to migrate', 'positional'),
        revision=('Schema revision to migrate to', 'option', 'm', str, None,
                  'REV')
    )
    def migrate(self, domain, revision='head'):
        self.api.execute_sync_task('put', self.get_url(domain),
                                   data={'action': 'migrate',
                                         'revision': revision})

    @plac.annotations(
        revision=('Schema revision to migrate to', 'option', 'm', str, None,
                  'REV')
    )
    def migrate_all(self, revision="head"):
        """ Migrate all instances at once """
        self.api.execute_sync_task('put', self.root_url,
                                   data={'action': 'migrate',
                                         'revision': revision})

    @plac.annotations(
        domain=('Instance domain', 'positional'),
        group=('The group to add to instance', 'positional')
    )
    def groups_add(self, domain, group):
        """ Add a group to an instance """
        url = self.get_url(domain, 'groups', group)
        self.api.put(url, data={})

    @plac.annotations(
        domain=('Instance domain', 'positional'),
        group=('The group to remove from instance', 'positional')
    )
    def groups_remove(self, domain, group):
        """ Remove a group from an instance.
            Instance's own group cannot be removed
        """
        url = self.get_url(domain, 'groups', group)
        self.api.delete(url)

    @plac.annotations(
        domain=('Instance domain', 'positional')
    )
    def groups_set(self, domain, *groups):
        """ Replace all groups with those on commandline.
            Instance's own group is always preserved
        """
        url = self.get_url(domain, 'groups')
        self.api.post(url, data={'groups': groups})

    @plac.annotations(
        domain=('Instance domain', 'positional')
    )
    def groups_empty(self, domain):
        """ Remove all groups from an instance,
            preserving instance's own group"""
        url = self.get_url(domain, 'groups')
        self.api.delete(url)

    @plac.annotations(
        domain=('Instance domain to check')
    )
    def allowed_users(self, domain):
        url = self.get_url(domain, 'users')
        response, content = self.api.get(url)
        content = content or {}
        for res in sorted(content):
            self.log.info(" • {}".format(res))
