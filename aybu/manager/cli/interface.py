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


class BaseInterface(object):

    def exit(self):
        raise plac.Interpreter.Exit

    def quit(self):
        self.exit()

    def __init__(self):
        self.commands.extend(['exit', 'quit'])
        if not hasattr(self, 'root_url'):
            self.root_url = '/{}'.format(self.name)

    @classmethod
    def init(cls, main, client):
        cls.main = main
        cls.api = client

    def get_url(self, *parts):
        url = self.root_url
        for part in parts:
            if not part.startswith("/"):
                part = "/{}".format(part)
            url = "{}{}".format(url, part)
        return url

    def remove(self, resource):
        self.api.delete(self.get_url(resource))

    def list(self):
        try:
            response, content = self.api.get(self.root_url)

        except ValueError:
            pass

        else:
            for res in content:
                print " * {}".format(res)

    def info(self, resource):
        try:
            response, content = self.api.get(self.get_url(resource))

        except ValueError:
            pass

        else:
            for k,v in content.iteritems():
                print "{}: {}".format(k, v)


