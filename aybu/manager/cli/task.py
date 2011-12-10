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


class TaskInterface(BaseInterface):

    commands = ['list', 'logs', 'delete', 'flush', 'info', 'flush_logs']
    name = 'tasks'

    def logs(self, task):
        response, content = self.api.get(self.get_url(task, 'logs'))

        if content:
            for log in content:
                print log.strip()

    def flush(self):
        self.api.delete(self.root_url, quiet=False)

    def flush_logs(self, task):
        self.api.delete(self.get_url(task, 'logs'), quiet=False)
