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
from collections import OrderedDict


class TaskInterface(BaseInterface):

    commands = ['list', 'logs', 'delete', 'flush', 'info', 'flush_logs']
    name = 'tasks'

    @plac.annotations(
        full=('Get complete output', 'flag', 'f'),
        verbose=('Be verbose', 'flag', 'v')
    )
    def list(self, full=False, verbose=False):
        quiet = not verbose
        response, content = self.api.get(self.root_url, quiet=quiet)
        content = content or {}
        ordered = OrderedDict(sorted(content.items(),
                                    key=lambda x: x[1]['requested']))
        if not full:
            for uid, data in ordered.iteritems():
                self.log.info(" • {} <{}> [{} - {}]".format(uid,
                                                    data['command'],
                                                    data['requested'],
                                                    data['status']))
        else:
            for uid, data in ordered.iteritems():
                self.log.info(" • {}:" .format(uid))
                self.print_info(data, prompt='   ° ')

    def logs(self, task):
        """ Show tasks logs """
        response, content = self.api.get(self.get_url(task, 'logs'))

        if content:
            for log in content:
                self.log.info(log.strip())

    def flush(self):
        self.api.delete(self.root_url, quiet=False)

    def flush_logs(self, task):
        self.api.delete(self.get_url(task, 'logs'), quiet=False)
