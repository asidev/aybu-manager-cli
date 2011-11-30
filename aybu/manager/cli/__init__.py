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

import logging
import os
import plac

from . instance import InstanceInterface
from . task import TaskInterface
from . environment import EnvironmentInterface
from . client import AybuManagerClient


class AybuManagerCliInterface(object):

    interfaces = (InstanceInterface, TaskInterface, EnvironmentInterface)

    def create_command_for_interface(self, intf):
        def command(*args, **kwargs):
            return self.dispatch(intf, *args, **kwargs)
        return command

    @plac.annotations(
        configfile=('Path to the config file', 'option', "f"),
        verbose=('Be verbose', 'flag', 'v')
    )
    def __init__(self, configfile, verbose):

        self.__doc__ = "\nUse help to see subcommands"
        self.configfile = configfile or '~/.aybu_manager_cli.conf'
        self.configfile = os.path.expanduser(self.configfile)
        self.loglevel = logging.INFO if not verbose else logging.DEBUG
        self.log = logging.getLogger('aybu')
        self.log.setLevel(self.loglevel)
        self.log.addHandler(logging.StreamHandler())

        self.commands = ['exit', 'quit']
        for intf in self.interfaces:
            setattr(self, intf.name, self.create_command_for_interface(intf))
            self.commands.append(intf.name)

    def __enter__(self):
        self.api_client = AybuManagerClient.create_from_config(self.configfile)
        return self

    def __exit__(self, etype, exc, tb):
        "Will be called automatically at the end of the intepreter loop"
        if etype in (None, GeneratorExit):  # success
            if self._interact_:
                print "exiting..."

    def dispatch(self, interface, *args):
        interface.init(main=self, client=self.api_client)
        if self._interact_:
            args = list(args)
            args.insert(0, "-i")
        plac.Interpreter.call(interface, verbose=True, arglist=args,
                              prompt="aybu «{}» > ".format(interface.name))
    def exit(self):
        raise plac.Interpreter.Exit

    def quit(self):
        self.exit()


def main():
    try:
        plac.Interpreter.call(AybuManagerCliInterface,
                            verbose=True, prompt='aybu> ')
    except KeyboardInterrupt:
        print "interrupted"


