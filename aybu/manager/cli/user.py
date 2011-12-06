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

    commands = ['list', 'create', 'update', 'info', 'delete']
    name = 'users'

    @plac.annotations(
        email=('User email. It will be used as username (required)', 'option',
               'e', str, None, 'EMAIL'),
        password=('User password (required)', 'option', 'p', str, None, 'PWD'),
        name=('User first name (required)', 'option', 'n', str, None, 'NAME'),
        surname=('User surname (required)', 'option', 's', str, None, 'SURNAME'),
        organization=('User company', 'option', 'o', str, None, 'COMPANY'),
        web=('User site address', 'option', 'a', str, None, 'HTTP_LINK'),
        twitter=('Username on twitter', 'option', 't', str, None, '@UNAME'),
        groups=('Comma separated list of groups the user belongs to. '
                'Every group must exists.',
                'option', 'g', str, None, 'GROUP[,GROUP..')
    )
    def create(self, email, password, name, surname, organization='',
               web='', twitter='', groups=[]):
        """ Create a new empty user """

        data = dict(
            email=email,
            password=password,
            name=name,
            surname=surname)
        if organization:
            data['organization'] = organization
        if web:
            data['web'] = web
        if twitter:
            data['twitter'] = twitter
        if groups:
            data['groups'] = comma_sep_to_list(groups)

        if not self.interactive and (not email or
                                     not password or
                                     not name or
                                     not surname):
            print "Missing required option"
            return

        elif self.interactive:
            for attr, prompt, convert, required in (
                        ('email', 'Email: ', str, True),
                        ('password', 'Password: ', str, True),
                        ('name', 'First Name: ', str, True),
                        ('surname', 'Surname: ', str, True),
                        ('organization', 'Company: ', str, False),
                        ('web', 'Web: ', str, False),
                        ('twitter', 'Twitter: ', str, False),
                        ('groups', 'Groups: ', comma_sep_to_list, False)
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
        user_email=('User to update', 'option', '-e', str, None, 'EMAIL')
    )
    def update(self, user_email, *attribute):
        """
        Update an user data. Attributes are the same as in users_create
        command, and they must be in the form arg=value
        """
        if not attribute:
            raise ValueError('Missing options')
        data = {}
        for attr in attribute:
            k, v = attr.split('=', 1)
            data[k] = v

        if 'groups' in data:
            data['groups'] = comma_sep_to_list(data['groups'])

        response, content = self.api.put(self.get_url(user_email), data=data)

        if content:
            for k,v in content.iteritems():
                print "{:<20}: {}".format(k,v)