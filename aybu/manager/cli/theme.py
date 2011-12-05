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

import re
import plac
from . interface import BaseInterface


class ThemeInterface(BaseInterface):

    commands = ['list', 'create', 'update', 'info', 'delete']
    name = 'themes'
    size_re = re.compile(r'([\d]+)[x]([\d]+)', re.IGNORECASE)

    def parse_size(self, size):
        w, h = self.size_re.match(size).groups()
        return int(w), int(h)

    @plac.annotations(
        name=('Theme name', 'option', '-t', str, None, 'NAME'),
        author=('Theme author email', 'option', '-a', str, None, 'EMAIL'),
        owner=('Theme owner email', 'option', '-o', str, None, 'EMAIL'),
        banner_size=('Banner WxH sizes (i.e 920x240)', 'option', '-b', str,
                       None, 'WIDTHxHEIGHT'),
        logo_size=('Logo WxH sizes (i.e 100x40)', 'option', '-l', str,
                       None, 'WIDTHxHEIGHT'),
        main_menu_levels= ('Main menu levels', 'option', '-L', int, None, 'NUM'),
        template_levels=('Max template levels', 'option', '-T', int, None,
                         'NUM'),
        image_width=('Image "full" width in pixels', 'option', '-I', str,
                         None, 'WIDTH'),
        version=('Theme version', 'option', '-V', str, None, 'VERSION'),
        parent=('Parent theme name (must exists)', 'option', '-p', str, None,
                'NAME')
    )
    def create(self, name, author, owner, banner_size, logo_size,
               main_menu_levels, template_levels, image_width, version=None,
               parent=None):

        banner_width, banner_height = self.parse_size(banner_size)
        logo_width, logo_height = self.parse_size(logo_size)
        data = dict(name=name,
                    author=author,
                    owner=owner,
                    banner_width=banner_width,
                    banner_height=banner_height,
                    logo_widht=logo_width,
                    logo_height=logo_height,
                    main_menu_levels=main_menu_levels,
                    template_levels=template_levels,
                    image_full_size=image_width)
        if parent:
            data['parent'] = parent
        if version:
            data['version'] = version

        response, content = self.api.post(self.get_url(), data)
        print response

    @plac.annotations(
        theme=('Theme to update', 'option', '-t', str, None, 'NAME')
    )
    def update(self, theme, **attribute):
        """
        Update a theme. attributes are the same as themes_create command, and
        must be in the form arg=value
        """
        if not attribute:
            raise ValueError('Missing options')
        data = {'name': theme}
        for attr in attribute:
            k, v = attr.split('=',1)
            data[k] = v

        response, content = self.api.post(self.get_url(theme), data)
        print response
        if not content:
            return
        for k, v in content.iteritems():
            print "{:<20}: {}".format(k, v)

