import os

FILE = os.environ.get('FILE', 'tests/input-file-test.csv')

DATA_STRUCTURE = "HTTP/1.1 {status_code} {status}\r\n" \
       "Content-Type: application/json; charset=utf-8" \
       "\r\n\r\n{body}\r\n\r\n"

INITIAL_DATA = [
       'GRU,BRC,10\n',
       'BRC,SCL,5\n',
       'GRU,CDG,75\n',
       'GRU,SCL,20\n',
       'GRU,ORL,56\n',
       'ORL,CDG,5\n',
       'SCL,ORL,20'
]
