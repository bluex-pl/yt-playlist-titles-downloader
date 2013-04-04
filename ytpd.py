#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##    ytpd - youtube playlist titles downloader
##    Copyright (C) 2013 Szymon Wroblewski
##
##    This library is free software; you can redistribute it and/or
##    modify it under the terms of the GNU Library General Public
##    License as published by the Free Software Foundation; either
##    version 2 of the License, or (at your option) any later version.
##
##    This library is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##    Library General Public License for more details.
##
##    You should have received a copy of the GNU Library General Public
##    License along with this library; if not, write to the Free
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
##    Szymon Wroblewski
##    bluex0@gmail.com

import sys
from requests import get
from urlparse import urlparse, parse_qs

api_url = 'http://gdata.youtube.com/feeds/api'


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else raw_input('URL: ')
    try:
        url_parts = urlparse(url)
        path_parts = url_parts.path.split('/')
        if path_parts[1] == 'user':
            print 'parsing user'
            parse_user(path_parts[2])
        elif path_parts[1] == 'playlist':
            print 'parsing playlist'
            parse_playlist(parse_qs(url_parts.query)['list'][0])
    except (KeyError, IndexError):
        print "unknown URL format"


def parse_user(user_id):
    url_template = '/'.join((api_url, 'users', user_id, 'playlists'))
    url_params = {
        'max-results': 50,
        #'prettyprint': 'true',
        'alt': 'jsonc',
        'v': '2',
    }
    print 'downloading'
    r = get(url_template, params=url_params)
    if r.status_code != 200:
        print r.text
        return
    data = r.json()['data']
    for item in data['items']:
        print 'playlist: {}'.format(item['title'])
        parse_playlist(item['id'])


def parse_playlist(playlist_id):
    url_template = '/'.join((api_url, 'playlists', playlist_id))
    url_params = {
        'start-index': 1,
        'max-results': 50,
        #'prettyprint': 'true',
        #'fields': 'entry(title)',
        'alt': 'jsonc',
        'v': '2',
    }
    current = 1
    total = 2
    f = None
    try:
        while current < total:
            print 'downloading'
            r = get(url_template, params=url_params)
            if r.status_code != 200:
                print r.text
                return
            data = r.json()['data']
            f = f if f is not None else open('{}.txt'.format(data['title']), 'w')
            for item in data['items']:
                f.write(item['video']['title'].encode('utf8') + '\n')
            current = data['startIndex'] + data['itemsPerPage']
            total = data['totalItems']
            url_params['start-index'] = current
    except KeyError as e:
        print "Data error: {}".format(e)
    finally:
        f.close()


if __name__ == '__main__':
    main()
