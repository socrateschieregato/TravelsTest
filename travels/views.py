from travels.exceptions import ErrorWriteFile
from travels.script import FindRoute, write_file
from settings import FILE


class Views:

    def __init__(self, route_data=None, file_data=None):
        self.data = file_data or FILE
        self.route = FindRoute(file_data=self.data)
        self.route_data = route_data

    def routes(self):
        from travels.helpers import to_json

        routes = self.route.get_rows_from_file()
        obj = to_json(routes)

        return obj

    def new_route(self):
        source = self.route_data['body']['source'].upper()
        destination = self.route_data['body']['destination'].upper()
        price = self.route_data['body']['price']

        if write_file(self.data, source, destination, price):
            return {
                'source': source,
                'destination': destination,
                'price': price
            }
        raise ErrorWriteFile('Error saving data')

    def get_route(self):
        route = FindRoute(
            self.route_data['query_params']['source'].upper(),
            self.route_data['query_params']['destination'].upper(),
            self.data
        )
        route.dijkstra()
        route.best_route()

        result = {
            'route': f"{route.source} - {' - '.join(route.path)}",
            'price': route.price
        }

        return result
