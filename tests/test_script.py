import logging
import mock
import os
import unittest
from getopt import GetoptError

from travels.exceptions import ErrorWriteFile
from travels.script import FindRoute, write_file, file_data_console
from settings import FILE

logger = logging.getLogger('backend')


class TestScript(unittest.TestCase):

    def setUp(self):
        self.graph = {
                'GRU': {
                    'BRC': 10,
                    'CDG': 75,
                    'SCL': 20,
                    'ORL': 56
                },
                'BRC': {
                    'SCL': 5
                },
                'SCL': {
                    'ORL': 20
                },
                'CDG': {},
                'ORL': {
                    'CDG': 5
                }
            }

    def test_get_rows_from_file(self):
        route = FindRoute(file_data=FILE)
        rows = route.get_rows_from_file()
        self.assertEqual(len(rows), 7)

    def test_get_rows_from_file_without_file(self):
        route = FindRoute()
        rows = route.get_rows_from_file()
        self.assertEqual(rows, None)

    def test_graph_from_file(self):
        route = FindRoute(file_data=FILE)
        graph = route.graph_from_file()
        self.assertEqual(
            graph,
            self.graph
        )

    def test_graph_from_file_with_no_exits_routes_graph_should_be_equal(self):
        route = FindRoute('ABC', 'DEF', FILE)
        graph = route.graph_from_file()
        self.assertEqual(graph, self.graph)

    def test_dijkstra_calculate_route(self):
        route = FindRoute('GRU', 'CDG', FILE)
        route.dijkstra()
        self.assertEqual(route.unseen_nodes, {})
        self.assertEqual(
            route.shortest_distance,
            {'GRU': 0, 'BRC': 10, 'SCL': 15, 'CDG': 40, 'ORL': 35}
        )
        self.assertEqual(
            route.predecessor,
            {'BRC': 'GRU', 'CDG': 'ORL', 'SCL': 'BRC', 'ORL': 'SCL'}
        )

    def test_best_route(self):
        route = FindRoute('GRU', 'CDG', FILE)
        route.dijkstra()
        best_route = route.best_route()
        result_string_expected = (
            f"best route: {route.source} - {' - '.join(route.path)}"
            f" > {route.shortest_distance[route.destination]}"
        )
        self.assertEqual(best_route, result_string_expected)

    def test_best_route_logs(self):
        with self.assertLogs('backend', level='INFO') as log:
            route = FindRoute('GRU', 'CDG', FILE)
            route.dijkstra()
            route.best_route()

        self.assertIn('best route: GRU - BRC - SCL - ORL - CDG > 40', log.output[0])

    def test_write_file(self):
        source, destination, price = ['ABC', 'DEF', 42]
        file = write_file('tests/write-file.csv', source, destination, price)

        assert file
        os.remove('tests/write-file.csv')

    def test_write_file_should_return_an_error(self):
        source, destination, price = ['ABC', 'DEF', None]
        with self.assertRaises(ErrorWriteFile):
            write_file('tests/write-file.csv', source, destination, price)

    def test_file_data_console(self):
        argv = ['tests/input-file-test.csv']
        file = file_data_console(argv)
        self.assertEqual(file, FILE)

    @mock.patch('sys.exit')
    def test_file_data_console_without_params(self, mock_sys):
        mock_sys.side_effect = GetoptError
        argv = []
        with self.assertRaises(Exception):
            with self.assertLogs('backend', level='ERROR') as log:
                file_data_console(argv)
        self.assertIn('Example: python script.py <input_file.csv>', log.output[0])
