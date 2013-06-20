#!/usr/bin/env python3
##    ytpd - youtube playlist titles downloader
##    Copyright (C) 2013 Szymon Wróblewski
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
##    Szymon Wróblewski
##    bluex0@gmail.com

import sys
import logging
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor
from requests import get

api_url = 'http://gdata.youtube.com/feeds/api'
api_params = {
    #'prettyprint': 'true',
    'alt': 'jsonc',
    'v': '2',
}

class DataError(Exception):
    pass


def get_json(*args, **kwargs):
    r = get(*args, **kwargs)
    if r.status_code != 200:
        logging.error(r.text)
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
        logging.info(('downloading {}/{}'.format(current, total)))
        part_params = dict(params, **{'start-index': current})
        data = get_json(url, params=part_params)['data']
        for item in data['items']:
            yield item


def parse_user(user_id):
    url = '/'.join((api_url, 'users', user_id, 'playlists'))
    try:
        items = parse_partial(url)
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(parse_playlist, (item['id'] for item in items))
    except KeyError as e:
        raise DataError from e


def parse_playlist(playlist_id):
    url = '/'.join((api_url, 'playlists', playlist_id))
    try:
        info = parse_info(url)
        logging.info('playlist: {title}'.format(**info))
        with open('{title}.txt'.format(**info), 'w', encoding='utf8') as f:
            items = parse_partial(url, total=info['totalItems'])
            f.writelines('{position}. {video[title]}\n'.format(**item) for item
                         in items)
    except KeyError as e:
        raise DataError from e


def main():
    logging.basicConfig(level=logging.INFO, style='{',
                        format='{levelname}:{thread}:{message}')
    logging.getLogger("requests").setLevel(logging.WARNING)
    url = sys.argv[1] if len(sys.argv) > 1 else input('URL: ')
    try:
        url_parts = urlparse(url)
        path_parts = url_parts.path.split('/')
        if path_parts[1] == 'user':
            logging.info('parsing user')
            parse_user(path_parts[2])
        elif path_parts[1] == 'playlist':
            logging.info('parsing playlist')
            parse_playlist(parse_qs(url_parts.query)['list'][0])
    except DataError:
        logging.exception('Data Error')
    except IndexError:
        logging.error('Invalid URL')


if __name__ == '__main__':
    main()
