from travels.views import Views

r = Views()

urls = [
    ('routes', r.routes),
    ('new_route', r.new_route),
    ('get_route', r.get_route)
]
