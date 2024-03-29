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
import inspect
import logging


class BaseInterface(object):

    def __init__(self, client, main_interface):
        self.log = logging.getLogger('aybu.manager.cli.{}'\
                                    .format(self.__class__.__name__))
        self.api = client
        self.main = main_interface
        if not hasattr(self, 'root_url'):
            self.root_url = '/{}'.format(self.name)

    @property
    def interactive(self):
        return self.main._interact_ if hasattr(self.main, '_interact_') \
                                    else False

    def get_completions(self, command, parts):
        """ This function get called during autocompletion.
            command is the command name, i.e.
            tasks_list <TAB> call this function
            on TaskInterface with "list" as command.
            parts is a list of kw to complete against
        """

        # first: if we have a get_${command}_completion call it
        attr = "get_{}_completions"
        try:
            return getattr(self, attr)(command, parts)

        except AttributeError:
            pass

        # use the default complete function
        return self.default_complete(command, parts)

    def default_complete(self, command, parts):
        """ This function is very simple: if command has a single argument
            we assume that it is self, so we do no completion at all.
            If the command has more than one arg, we can't know what to do,
            so we do nothing.
            Else autocomplete on primary keys, i.e. call get_list()
        """

        kw = parts[0]
        try:
            argsspec = inspect.getargspec(getattr(self, command))
            num_non_kw_params = len(argsspec.args)
            if argsspec.defaults:
                num_non_kw_params = num_non_kw_params - len(argsspec.defaults)
            if num_non_kw_params == 1:
                return []

        except AttributeError:
            return []

        # string startswith themselves, avoid replication
        res = set(self.get_list(quiet=True, debug=False))
        if kw in res:
            return []

        return [w for w in res if w.startswith(kw)]

    def get_url(self, *parts):
        url = self.root_url
        for part in parts:
            if not part.startswith("/"):
                part = "/{}".format(part)
            url = "{}{}".format(url, part)
        return url

    def get_list(self, quiet=False, debug=None):
        kwargs = dict(quiet=quiet)
        if not debug is None:
            kwargs['debug'] = debug
        try:
            response, content = self.api.get(self.root_url, **kwargs)

        except ValueError:
            return []

        else:
            return content.keys()

    def print_info(self, content, prompt=''):
        if not content:
            return
        max_len = max({len(k) for k in content})
        max_len = 30 if max_len < 30 else max_len
        format_string = unicode("{}{:<%d}: {}" % (max_len))

        for attr in sorted(content.keys()):
            key = attr
            if key.startswith("__"):
                continue
            if attr.startswith("_"):
                key = attr[1:]
            cont = content[attr]
            if isinstance(cont, list):
                cont = ", ".join([str(e) for e in cont])
            self.log.info(format_string.format(prompt, key, cont))

    @plac.annotations(
        full=('Get complete output', 'flag', 'f'),
        verbose=('Be verbose', 'flag', 'v')
    )
    def list(self, full=False, verbose=False):
        quiet = not verbose
        response, content = self.api.get(self.root_url, quiet=quiet)
        content = content or {}
        for res in sorted(content):
            self.log.info(" • {}".format(res))
            if full:
                self.print_info(content[res], prompt='   ° ')

    @plac.annotations(
        resource=('The resource to operate on', 'positional')
    )
    def info(self, resource):
        """ Get the info of the given resource """
        response, content = self.api.get(self.get_url(resource))
        self.print_info(content)

    @plac.annotations(
        resource=('The resource to operate on', 'positional')
    )
    def delete(self, resource):
        """ Delete the selected resource """
        self.api.delete(self.get_url(resource), quiet=False)
