from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length'))
        data = self.rfile.read(length).decode()

        sender_ip = self.client_address[0]

        filename = f"Box/{sender_ip}.txt"

        with open(filename, "w") as f:
            f.write(data)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

server = HTTPServer(("0.0.0.0", 8080), Handler)
print("Listening on port 8080...")
server.serve_forever()
