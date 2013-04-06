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
api_params = {
    #'prettyprint': 'true',
    'alt': 'jsonc',
    'v': '2',
}


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


def get_json(*args, **kwargs):
    r = get(*args, **kwargs)
    if r.status_code != 200:
        print r.text
        return {}
    return r.json()


def parse_info(url, params={}):
    params = dict(api_params, **params)
    params['max-results'] = 0
    return get_json(url, params=params)['data']


def parse_partial(url, params={}, start=1, total=None, ipp=50):
    params = dict(api_params, **params)
    params['max-results'] = ipp
    total = parse_info(url, params)['totalItems'] if total is None else total
    for current in range(start, total, ipp):
        print 'downloading {}/{}'.format(current, total)
        part_params = dict(params, **{'start-index': current})
        data = get_json(url, params=part_params)['data']
        for item in data['items']:
            yield item


def parse_user(user_id):
    url = '/'.join((api_url, 'users', user_id, 'playlists'))
    try:
        items = parse_partial(url)
        for item in items:
            print 'playlist: {title}'.format(**item)
            parse_playlist(item['id'])
    except KeyError as e:
        print 'Data error: {}'.format(e)


def parse_playlist(playlist_id):
    url = '/'.join((api_url, 'playlists', playlist_id))
    try:
        info = parse_info(url)
        f = open('{title}.txt'.format(**info), 'w')
        items = parse_partial(url, total=info['totalItems'])
        for item in items:
            f.write(item['video']['title'].encode('utf8') + '\n')
    except KeyError as e:
        print 'Data error: {}'.format(e)
    finally:
        f.close()


if __name__ == '__main__':
    main()
