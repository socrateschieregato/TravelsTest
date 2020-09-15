import json
import unittest
from socket import socket, AF_INET, SOCK_STREAM

from travels.script import FindRoute
from settings import FILE, INITIAL_DATA


def remove_last_line():
    with open(FILE, 'w') as f:
        for row in INITIAL_DATA:
            f.writelines(row)


class TestApi(unittest.TestCase):

    def setUp(self):
        self.client_socket = socket(AF_INET, SOCK_STREAM)

    def tearDown(self):
        self.client_socket.close()

    def test_routes(self):
        self.client_socket.connect(('localhost', 8000))
        self.client_socket.send('GET /routes HTTP/1.1\r\n\r\n'.encode())
        response = (self.client_socket.recv(1024).decode()).strip().split('\r\n')
        protocol, status_code, status = response[0].split()
        data = json.loads(response[-1].replace('\'', '\"'))

        self.assertEqual(int(status_code), 200)
        self.assertEqual(len(data), 7)
        self.assertEqual(data[0]['source'], 'GRU')
        self.assertEqual(data[-1]['source'], 'SCL')

    def test_get_route_gru_cdg(self):
        self.client_socket.connect(('localhost', 8000))
        self.client_socket.send(
            'GET /get_route?source=gru&destination=CDG HTTP/1.1\r\n\r\n'.encode()
        )
        response = (self.client_socket.recv(1024).decode()).strip().split('\r\n')
        protocol, status_code, status = response[0].split()
        data = json.loads(response[-1].replace('\'', '\"'))

        self.assertEqual(data, {'route': 'GRU - BRC - SCL - ORL - CDG', 'price': 40})
        self.assertEqual(int(status_code), 200)
        self.assertEqual(len(data), 2)

    def test_get_route_not_in_file(self):
        self.client_socket.connect(('localhost', 8000))
        self.client_socket.send(
            'GET /get_route?source=ABC&destination=XYZ HTTP/1.1\r\n\r\n'.encode()
        )
        response = (self.client_socket.recv(1024).decode()).strip().split('\r\n')
        protocol, status_code, status = response[0].split()
        data = json.loads(response[-1].replace('\'', '\"'))

        self.assertEqual(data, {'detail': 'BAD_REQUEST'})
        self.assertEqual(int(status_code), 400)

    def test_new_route(self):
        self.client_socket.connect(('localhost', 8000))
        self.client_socket.send(
            'POST /new_route HTTP/1.1\r\n\r\n'
            '{\n\t"source": "ABC",\n\t"destination": "DEF",\n\t"price": 35\n}'.encode()
        )
        response = (self.client_socket.recv(1024).decode()).strip().split('\r\n')
        protocol, status_code, status = response[0].split()
        data = json.loads(response[-1].replace('\'', '\"'))

        self.assertEqual(data, {'source': 'ABC', 'destination': 'DEF', 'price': 35})
        self.assertEqual(int(status_code), 201)
        remove_last_line()

    def test_get_route_gru_cdg(self):
        route = FindRoute('GRU', 'CDG', FILE)
        route.dijkstra()
        route.best_route()

        self.assertEqual(
            route.result,
            {
                'route': 'GRU - BRC - SCL - ORL - CDG',
                'price': 40
            }
        )

    def test_get_route_brc_cdg(self):
        route = FindRoute('BRC', 'CDG', FILE)
        route.dijkstra()
        route.best_route()

        self.assertEqual(
            route.result,
            {
                'route': 'BRC - SCL - ORL - CDG',
                'price': 30
            }
        )

    def test_get_route_brc_cdg_with_lowercase(self):
        route = FindRoute('brc', 'cdg', FILE)
        route.dijkstra()
        route.best_route()

        self.assertEqual(
            route.result,
            {
                'route': 'BRC - SCL - ORL - CDG',
                'price': 30
            }
        )

    def test_get_route_without_source(self):
        route = FindRoute('', 'cdg', FILE)
        route.dijkstra()
        route.best_route()

        self.assertEqual(
            route.result,
            {}
        )

    def test_get_route_without_destination(self):
        route = FindRoute('brc', '', FILE)
        route.dijkstra()
        route.best_route()

        self.assertEqual(
            route.result,
            {}
        )

    def test_get_route_without_file(self):
        route = FindRoute('brc', 'cdg')
        route.dijkstra()
        route.best_route()

        self.assertEqual(
            route.result,
            {}
        )
