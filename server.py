import logging
from socket import (
    AF_INET,
    socket,
    SOCK_STREAM,
    SHUT_WR
)

from travels.exceptions import NotFoundException
from travels.helpers import route_data_or_404, get_view
from settings import DATA_STRUCTURE

logger = logging.getLogger('backend')


class Server:

    def create_server(self):
        try:
            server = socket(AF_INET, SOCK_STREAM)
            server.bind(('localhost', 8000))
            server.listen(5)

            while True:
                (client_socket, address) = server.accept()
                rd = client_socket.recv(5000).decode()
                pieces = rd.split('\r\n')
                if len(pieces) > 0:
                    print(pieces[0])

                try:
                    route_data = route_data_or_404(pieces)
                    body = get_view(route_data)
                    if body and route_data['method'] == 'POST':
                        status_code = 201
                    else:
                        status_code = 200

                    data = DATA_STRUCTURE.format(
                        status_code=status_code,
                        status='OK',
                        body=body if body else ''
                    )
                    client_socket.send(bytes(data, 'utf-8'))

                except NotFoundException as e:
                    data = DATA_STRUCTURE.format(
                        status_code=404,
                        status='NOT_FOUND',
                        body={'detail': "NOT_FOUND"}
                    )
                    client_socket.send(bytes(data, 'utf-8'))
                    logger.error(f"Erro: {e}")

                except Exception as e:
                    data = DATA_STRUCTURE.format(
                        status_code=400,
                        status='BAD_REQUEST',
                        body={'detail': "BAD_REQUEST"}
                    )
                    client_socket.send(bytes(data, 'utf-8'))
                    logger.error(f"Erro: {e}")
                finally:
                    client_socket.shutdown(SHUT_WR)

        except KeyboardInterrupt:
            logger.info("\nShutting down...\n")
        finally:
            server.close()


print('Server up and running on:  http://localhost:8000')
server = Server()
server.create_server()
