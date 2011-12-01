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


import ConfigParser
import json
import logging
import os
import platform
import requests
import zmq

log = logging.getLogger(__name__)


class AybuManagerClient(object):

    def __init__(self, host, subscription_addr,
                 username=None, password=None, timeout=None):

        self.host = host
        self.username = username
        self.password = password
        self.sub_addr = subscription_addr
        self.zmq_context = zmq.Context()
        self.zmq_response_socket = self.zmq_context.socket(zmq.SUB)
        self.zmq_response_socket.connect(self.sub_addr)
        self.counter = 0
        self.config = None
        self.auth_info = None if not username or not password \
                         else (username, password)
        self.timeout = timeout

    @classmethod
    def create_from_config(cls, configfile, overrides={}):
        config = ConfigParser.ConfigParser()
        try:
            with open(configfile) as f:
                config.readfp(f)

        except IOError as e:
            log.critical("Cannot read config file: {}".format(e))
            raise

        kwargs = {}
        for var in ('username', 'password', 'host', 'subscription_addr',
                    'timeout'):
            try:
                kwargs[var] = config.get('remote', var, vars=overrides)
            except:
                if var in ('host', 'subscription_addr'):
                    log.critical("No variable '%s' for api client.".format(var))
                    raise TypeError('Missing configuration for {}'.format(var))

        obj = cls(**kwargs)
        obj.config = config
        return obj

    def uuid(self):
        uuid = '{}.{}-{}'.format(platform.uname()[1], os.getpid(), self.counter)
        self.zmq_response_socket.setsockopt(zmq.SUBSCRIBE, uuid)
        return uuid

    def url(self, path_info):
        return "{}{}".format(self.host, path_info)

    def request(self, method, url, *args, **kwargs):
        url = self.url(url)

        auth = kwargs.pop('auth', self.auth_info)
        timeout = kwargs.pop('timeout', self.timeout)
        kwargs.update(dict(timeout=timeout, auth=auth))

        quiet = kwargs.pop('quiet', False)
        if not quiet:
            log.info("%s %s", method.upper(), url)

        response = requests.request(method, url, *args, **kwargs)
        try:
            response.raise_for_status()

        except Exception as e:
            if not quiet:
                log.error("%s: %s", response.status_code, e)

        else:
            if not quiet:
                log.debug(response)

        return response

    def post(self, url, data, **kwargs):
        return self.request('post', url, data=data, **kwargs)

    def put(self, url, data, **kwargs):
        return self.request('put', url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('delete', url, **kwargs)

    def head(self, url, **kwargs):
        return self.request('head', url, **kwargs)

    def get(self, url, **kwargs):
        response = self.request('get', url, **kwargs)
        return response, json.loads(response.content)

    def execute_task(self, method, *args, **kwargs):
        try:
            uuid = self.uuid()
            headers = {'X-Task-UUID': uuid}
            response = self.request(method, *args, headers=headers, **kwargs)
            response.raise_for_status()

            log.info("Task {}: {}".format(response.headers['x-task-uuid'],
                                        response.headers['x-task-status']))
            return response

        finally:
            self.counter = self.counter + 1

    def execute_sync_task(self, method, *args, **kwargs):
        try:
            response = self.execute_task(method, *args, **kwargs)

            if response.headers['x-task-status'] == 'DEFERRED':
                return response

            while True:
                try:
                    message = self.zmq_response_socket.recv_multipart()
                    topic, msg = message
                    msg = msg.strip()

                except KeyboardInterrupt:
                    raise

                except:
                    log.exception("Error while reading from subscription")
                    continue

                topic_parts = topic.split(".")
                topic = '.'.join(topic_parts)

                try:
                    level = topic_parts[-1:][0]
                    getattr(log, level.lower())("%s: %s", topic, msg)

                except (AttributeError, IndexError):
                    if level == 'finished':
                        raise KeyboardInterrupt
                    log.info("%s: %s", topic, msg)

        except KeyboardInterrupt:
            pass

