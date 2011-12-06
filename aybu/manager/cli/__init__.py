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
from . theme import ThemeInterface
from . group import GroupInterface
from . user import UserInterface
from . client import AybuManagerClient
from . autocomplete import AybuManagerCliReadline


class AybuManagerCliInterface(object):

    interfaces = (InstanceInterface, TaskInterface, EnvironmentInterface,
                  ThemeInterface, GroupInterface, UserInterface)
    interface_instances = {}
    commands = set(('exit', 'quit', 'help_commands'))

    def create_commands_for_interface(self, intf_cls):
        interface = intf_cls(self.api_client, self)
        self.__class__.interface_instances[intf_cls.name] = interface
        for command in interface.commands:
            command_name = "{}_{}".format(intf_cls.name, command)
            setattr(self, command_name, getattr(interface, command))
            self.__class__.commands.add(command_name)

    @plac.annotations(
        configfile=('Path to the config file', 'option', "F"),
        verbose=('Be verbose', 'flag', 'V')
    )
    def __init__(self, configfile, verbose):

        self.__doc__ = "\nUse help to see subcommands"
        self.configfile = configfile or '~/.aybu_manager_cli.conf'
        self.configfile = os.path.expanduser(self.configfile)
        self.loglevel = logging.INFO if not verbose else logging.DEBUG
        self.log = logging.getLogger('aybu')
        self.log.setLevel(self.loglevel)
        self.log.addHandler(logging.StreamHandler())
        self.api_client = AybuManagerClient.create_from_config(self.configfile)

        for intf in self.interfaces:
            self.create_commands_for_interface(intf)

    def __enter__(self):
        return self

    def __exit__(self, etype, exc, tb):
        "Will be called automatically at the end of the intepreter loop"
        if etype in (None, GeneratorExit):  # success
            if self._interact_:
                print "exiting..."

    def exit(self):
        raise plac.Interpreter.Exit

    def quit(self):
        self.exit()

    def help_commands(self):
        print " ".join([c for c in self.commands if c not in ("help",
                                                              "help_commands",
                                                              "exit",
                                                              ".last_tb",
                                                              "quit")])


def main():
    try:
        histfile = os.path.expanduser('~/{}.history'.format(__name__))
        completer = AybuManagerCliReadline(histfile=histfile,
                                           factory=AybuManagerCliInterface)
        plac.Interpreter.call(AybuManagerCliInterface,
                              stdin=completer, verbose=True, prompt='aybu> ')
    except KeyboardInterrupt:
        print "interrupted"


