#!/usr/bin/python
import logging
import sys
import getopt

from travels.exceptions import ErrorWriteFile

logger = logging.getLogger('backend')


class FindRoute:

    def __init__(self, source=None, destination=None, file_data=None):
        self.source = source.upper() if source else None
        self.destination = destination.upper() if destination else None
        self.price = 0
        self.data = file_data
        self.graph = self.graph_from_file()
        self.path = []
        self.shortest_distance = {}
        self.predecessor = {}
        self.unseen_nodes = self.graph.copy()
        self.infinity = 999999
        self.result = {}

    def get_rows_from_file(self):
        if self.data:
            rows = []
            with open(self.data, 'r') as f:
                reader = f.readlines()
                for row in reader:
                    rows.append(row.strip().split(','))
            return rows

    def graph_from_file(self):
        rows = self.get_rows_from_file() or []
        graph = {}
        for row in rows:
            source, destination, price = row
            if source not in graph:
                graph[source] = {}
            if not graph.get(destination):
                graph[destination] = {}
            graph[source][destination] = int(price)

        return graph

    def dijkstra(self):
        for node in self.unseen_nodes:
            self.shortest_distance[node] = self.infinity
        self.shortest_distance[self.source] = 0
        self.calculate_route()

    def calculate_route(self):
        while self.unseen_nodes:
            min_node = None
            for node in self.unseen_nodes:
                if min_node is None or self.shortest_distance[node] < self.shortest_distance[min_node]:
                    min_node = node

            for child_node, price in self.graph[min_node].items():
                if price + self.shortest_distance[min_node] < self.shortest_distance[child_node]:
                    self.shortest_distance[child_node] = price + self.shortest_distance[min_node]
                    self.predecessor[child_node] = min_node

            self.unseen_nodes.pop(min_node)

    def best_route(self):
        current_node = self.destination or self.source
        prerequisites = bool(self.source and self.destination and self.data)
        while current_node != self.source:
            try:
                self.path.insert(0, current_node)
                current_node = self.predecessor[current_node]
            except KeyError:
                logger.info('Path not reachable')
                break
        if prerequisites and self.shortest_distance[self.destination] != self.infinity:
            self.price = self.shortest_distance[self.destination]
            self.result = {
                'route': f"{self.source} - {' - '.join(self.path)}",
                'price': (self.shortest_distance[self.destination])
            }
            result_string = (
                f"best route: {self.source} - {' - '.join(self.path)}"
                f" > {self.shortest_distance[self.destination]}"
            )
            logger.info(result_string)
            return result_string


def file_data_console(argv):
    error_message = 'Example: python script.py <input_file.csv>'
    try:
        _, input_file = getopt.getopt(argv, None)
        if not input_file:
            raise getopt.GetoptError(error_message)
    except getopt.GetoptError:
        logger.error(error_message)
        sys.exit(2)

    return input_file[0]


def write_file(file, source, destination, price):
    try:
        logger.info('Starting to save in csv file')
        if bool(source and destination and price):
            new_entry = f'{source},{destination},{str(price)}'
            with open(file, 'a+') as f:
                f.write('\n')
                f.write(new_entry)
                f.close()
            logger.info('Data saved in csv with success!')
            return True
        else:
            raise ErrorWriteFile
    except Exception:
        raise ErrorWriteFile


if __name__ == "__main__":
    option = 1
    while option != 0:
        input_data = input('please enter the route: ')
        if not input_data:
            break
        input_data = input_data.upper().split('-')
        file_data = file_data_console(sys.argv[1:])
        route = FindRoute(input_data[0], input_data[1], file_data=file_data)
        route.dijkstra()
        print(route.best_route())
