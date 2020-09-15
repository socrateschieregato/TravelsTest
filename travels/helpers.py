import json
import logging
import urllib.parse

from travels.exceptions import NotFoundException
from travels.urls import urls, Views

logger = logging.getLogger('backend')


def route_data_or_404(pieces):
    try:
        method, url_data, protocol = pieces[0].strip().split()
        query_params = {}
        if '?' in url_data:
            url_data, query_params_data = url_data.split('?')
            query_params = dict(urllib.parse.parse_qsl(query_params_data))

        url = url_data.replace('/', '')
        body = json.loads(pieces[-1].replace('\n\t', '')) if pieces[-1] != '' else None
        route_data = {
            'method': method,
            'url': url,
            'body': body,
            'protocol': protocol,
            'query_params': query_params if query_params else None
        }
        logger.info(route_data)

        return route_data
    except Exception as e:
        raise NotFoundException(f'Error to decode request: {e}')


def get_view(route_data):
    for r in urls:
        if route_data['url'] == r[0]:
            method = getattr(
                Views(route_data),
                r[0],
                lambda: True
            )
            logger.info(f'View: {r[0]}')
            return method()

    raise NotFoundException('Page not Found')


def to_json(routes):
    routes_dict = []
    obj = {}
    for route in routes:
        obj['source'] = route[0]
        obj['destination'] = route[1]
        obj['price'] = int(route[2])
        routes_dict.append(obj.copy())
    return routes_dict
