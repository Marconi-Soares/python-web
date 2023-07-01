from urllib.parse import urlparse, parse_qs
import http.server
import socketserver
import json


PORT = 8000


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def default_response(self, *args, **kwargs):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        json_response = json.dumps({"message": "Hello, World!"})
        return self.wfile.write(json_response.encode())
        
    def greeting(self, query):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        name = query["name"][0]
        response = {'msg': f'Hello, {name}'}
        json_response = json.dumps(response)

        self.wfile.write(json_response.encode())

    def get_route(self):
        url_parts = urlparse(self.path)
        query_params = parse_qs(url_parts.query)

        if url_parts.path == '/hello' and 'name' in query_params:
            return self.greeting, query_params
        
        return self.default_response, None

    def do_GET(self):
        func, params = self.get_route()
        print(params)
        return func(params)


with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
    print("Server running in port:", PORT)
    httpd.serve_forever()

