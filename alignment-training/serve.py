#! /usr/bin/python3

import http.server

PORT = 8000

address = ('', PORT)

server = http.server.HTTPServer(address, http.server.SimpleHTTPRequestHandler)

print(f"Serving at http://localhost:{PORT}/main.html")

server.serve_forever()
