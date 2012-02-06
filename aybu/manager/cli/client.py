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

import ast
import ConfigParser
import json
import logging
import os
import platform
import requests
import httplib
import sys
import zmq

log = logging.getLogger(__name__)


class AybuManagerClient(object):
    log = log

    def __init__(self, host, subscription_addr,
                 username=None, password=None, timeout=None,
                 debug=False, verify_ssl=False):

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
        self.debug = debug
        self.verify_ssl = verify_ssl
        if debug:
            self.log.debug("Created client for {} (user: {}, sub: {})"\
                    .format(self.host, self.username, self.sub_addr))

    @staticmethod
    def status_code_to_string(status_code):
        return httplib.responses[status_code]

    @classmethod
    def create_from_config(cls, configfile, debug=False,
                           remote='default',
                           overrides={}):
        config = ConfigParser.ConfigParser()
        cls.log.debug("Reading config from %s, remote <%s>",
                      configfile, remote)
        try:
            with open(configfile) as f:
                config.readfp(f)

        except IOError as e:
            cls.log.critical("Cannot read config file: {}".format(e))
            raise

        kwargs = {'debug': debug}
        for var in ('username', 'password', 'host', 'subscription_addr',
                    'timeout', 'verify_ssl'):
            try:
                kwargs[var] = config.get(remote, var, vars=overrides)
                if var == 'verify_ssl':
                    kwargs[var] = ast.literal_eval(kwargs[var])

            except ValueError:
                cls.log.error("{} has invalid value {}, assuming None"\
                               .format(var, kwargs[var]))
                del kwargs[var]

            except:
                if var in ('host', 'subscription_addr'):
                    log.critical("No variable '%s' for api client.", var)
                    raise TypeError('Missing configuration for {}'.format(var))

        obj = cls(**kwargs)
        obj.config = config
        return obj

    def uuid(self):
        uuid = '{}.{}-{}'.format(platform.uname()[1],
                                 os.getpid(),
                                 self.counter)
        self.zmq_response_socket.setsockopt(zmq.SUBSCRIBE, uuid)
        return uuid

    def url(self, path_info):
        return "{}{}".format(self.host, path_info)

    def print_headers(self, headers):
        self.log.debug("Headers: ")
        for h in sorted(headers):
            self.log.debug(" {:<20}: {}".format(h.title(), headers[h]))

    def request(self, method, url, *args, **kwargs):
        url = self.url(url)

        auth = kwargs.pop('auth', self.auth_info)
        timeout = kwargs.pop('timeout', self.timeout)
        kwargs.update(dict(timeout=timeout, auth=auth))
        kwargs.update(dict(verify=self.verify_ssl))

        quiet = kwargs.pop('quiet', False)
        debug = self.debug or kwargs.pop('debug', False)

        if debug:
            quiet = False

        try:
            response = requests.request(method, url, *args, **kwargs)

        except requests.exceptions.RequestException as e:
            self.log.critical("Error connection to API: {} - {}"\
                               .format(type(e).__name__, e))
            return None, None

        try:
            response.raise_for_status()

        except Exception:
            self.log.error("Error in response: {} {}".format(
                        response.status_code,
                        self.status_code_to_string(response.status_code)))
            if 'x-request-error' in response.headers:
                self.log.error("Message: {}"\
                        .format(response.headers['x-request-error']))

            self.print_headers(response.headers)

            return response, None

        else:
            self.print_headers(response.headers)

            if not quiet:
                self.log.info("OK {} {}".format(response.status_code,
                            self.status_code_to_string(response.status_code)))
            try:
                content = json.loads(response.content)
                if self.log.getEffectiveLevel() == logging.DEBUG and not quiet:
                    sys.stderr.write(json.dumps(content,
                                                sort_keys=True,
                                                indent=4))
                    sys.stderr.write("\n\n")
                    sys.stderr.flush()

            except (AttributeError, ValueError) as e:
                if int(response.headers['content-length']) != 0:
                    self.log.error("Cannot decode json: %s", e)
                content = None

            return response, content

    def post(self, url, data, **kwargs):
        return self.request('post', url, data=data, **kwargs)

    def put(self, url, data, **kwargs):
        return self.request('put', url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('delete', url, **kwargs)

    def head(self, url, **kwargs):
        return self.request('head', url, **kwargs)

    def get(self, url, **kwargs):
        return self.request('get', url, **kwargs)

    def execute_task(self, method, *args, **kwargs):
        try:
            uuid = self.uuid()
            headers = {'X-Task-UUID': uuid}
            response, content = self.request(method, *args, headers=headers,
                                             **kwargs)
            if response:
                response.raise_for_status()

                log.info("Task {}: {}".format(response.headers['x-task-uuid'],
                                            response.headers['x-task-status']))
            return response

        finally:
            self.counter = self.counter + 1

    def execute_sync_task(self, method, *args, **kwargs):
        try:
            response = self.execute_task(method, *args, **kwargs)
            if not response:
                return

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
