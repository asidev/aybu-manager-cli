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

class AybuManagerCliReadline(plac.ReadlineInput):

    def __init__(self, factory, histfile=None):
        self.factory = factory
        super(AybuManagerCliReadline, self).__init__([], histfile=histfile)

    def complete(self, kw, state):
        current_line = self.rl.get_line_buffer()
        parts = current_line.split(" ")
        nparts = len(parts)

        if nparts == 1:
            # complete commands
            completions = [c for c in self.factory.commands if c.startswith(kw)]

        elif nparts == 2:
            # demand completion to interface
            inst_name, inst_command = parts[0].split("_", 1)
            inst = self.factory.interface_instances[inst_name]
            completions = inst.get_completions(inst_command, parts[1:])

        else:
            return

        try:
            return completions[state]

        except IndexError:
            return
