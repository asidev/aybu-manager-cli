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

import getpass
import plac
from . interface import BaseInterface


def comma_sep_to_list(string):
    return string.split(",")


class UserInterface(BaseInterface):

    commands = ['list', 'create', 'update', 'info', 'delete', 'check_login',
                'allowed_instances']
    name = 'users'

    @plac.annotations(
        email=('User email. It will be used as username', 'positional'),
        password=('User password (required)', 'option', 'p', str, None, 'PWD'),
        name=('User first name (required)', 'option', 'n', str, None, 'NAME'),
        surname=('User surname (required)', 'option', 's', str, None,
                 'SURNAME'),
        company=('User company', 'option', 'C', str, None, 'COMPANY'),
        web=('User site address', 'option', 'a', str, None, 'HTTP_LINK'),
        twitter=('Username on twitter', 'option', 't', str, None, '@UNAME'),
        groups=('Comma separated list of groups the user belongs to. '
                'Every group must exists.',
                'option', 'G', str, None, 'GROUP[,GROUP..'),
        organization=('Organization group for the user (it must exists)',
                       'option', 'o', str, None, 'ORGANIZATION')
    )
    def create(self, email, password, name, surname, company='',
               web='', twitter='', groups=[], organization=None):
        """ Create a new empty user """

        data = dict(
            email=email,
            password=password,
            name=name,
            surname=surname)
        if company:
            data['company'] = company

        if web:
            data['web'] = web

        if twitter:
            data['twitter'] = twitter

        if groups:
            data['groups'] = comma_sep_to_list(groups)

        if organization:
            data['organization'] = organization

        if not self.interactive and (not email or
                                     not password or
                                     not name or
                                     not surname):
            self.log.error("Missing required option")
            return

        elif self.interactive:
            for attr, prompt, convert, required in (
                        ('email', 'Email: ', str, True),
                        ('password', 'Password: ', str, True),
                        ('name', 'First Name: ', str, True),
                        ('surname', 'Surname: ', str, True),
                        ('company', 'Company: ', str, False),
                        ('web', 'Web: ', str, False),
                        ('twitter', 'Twitter: ', str, False),
                        ('groups', 'Groups: ', comma_sep_to_list, False),
                        ('organization', 'Organization: ', str, False)
            ):
                if required and not data[attr]:
                    if attr == "password":
                        data[attr] = convert(getpass.getpass(prompt).strip())

                    else:
                        data[attr] = convert(raw_input(prompt).strip())

                elif not required and not attr in data:
                    value = convert(raw_input(prompt).strip())
                    if value:
                        data[attr] = value

        self.api.post(self.get_url(), data)

    @plac.annotations(
        email=('User to update', 'positional')
    )
    def update(self, email, *attribute):
        """
        Update an user data. Attributes are the same as in users_create
        command, and they must be in the form arg=value.
        To update user's groups, you *must* list ALL his/her new groups
        as a comma-separated list, i.e. groups=admin,asidev,newgroup
        """
        if not attribute:
            raise ValueError('Missing options')
        data = {}
        for attr in attribute:
            k, v = attr.split('=', 1)
            data[k] = v

        if 'groups' in data:
            data['groups'] = comma_sep_to_list(data['groups'])

        response, content = self.api.put(self.get_url(email), data=data)

        if content:
            for k, v in content.iteritems():
                self.log.info(unicode("{:<20}: {}").format(k, v))

    @plac.annotations(
        domain=('Site domain', 'positional'),
        email=('User to check', 'option', 'u')
    )
    def check_login(self, domain, email=None):
        if not email:
            email = self.api.username

        res, content = self.api.get("{}?action=login&domain={}"\
                                    .format(self.get_url(email),
                                            domain))
        if content:
            for k, v in content.iteritems():
                self.log.info(unicode("{:<20}: {}").format(k, v))

    @plac.annotations(
        email=('User email', 'positional')
    )
    def allowed_instances(self, email):
        url = self.get_url(email, 'instances')
        response, content = self.api.get(url)
        content = content or {}
        for res in sorted(content):
            self.log.info(" • {}".format(res))
