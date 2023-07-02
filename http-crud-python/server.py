import json
import socketserver
from db.sqlite import Tasks
from urllib.parse import urlparse, parse_qs
from http.server import SimpleHTTPRequestHandler


Tasks.migrate()


PORT = 8000
class Server(SimpleHTTPRequestHandler):
    def task_create(self, data):
        Tasks.add(**data)
        self.response(status=201, data={})

    def task_update(self, title, id):
        task = Tasks.update(title, id)
        self.response(task)

    def task_list(self, query):
        if query is None: 
            return self.response(Tasks.all())
        return Tasks.filter(title=query[0])
    
    def task_retrieve(self, id):
        try: 
            self.response(Tasks.get(id))
        except: 
            self.send_error(404)

    def task_destroy(self, id):
        Tasks.delete(id)
        return self.response(status=204, data={})
    
    def do_GET(self):
        query_params = parse_qs(urlparse(self.path).query).get('title')
        route = urlparse(self.path).path

        if route in ['/tasks', '/tasks/']:
            self.task_list(query_params)
        else:
            id = route.split('/')[-1]
            self.task_retrieve(id)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_POST(self):
        self.task_create(self.data)

    def do_PATCH(self):
        route = urlparse(self.path).path
        id = route.split('/')[-1]

        try:
            title = self.data.get('title')
            self.task_update(title, id)
        except:
            self.send_error(400)

    @property
    def data(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)
        return data


    def response(self, data, status=200):
        self.send_response(status)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        json_response = json.dumps(data)
        self.wfile.write(json_response.encode())


with socketserver.TCPServer(("", PORT), Server) as httpd:
    print('Server running in port', PORT)
    httpd.serve_forever()

