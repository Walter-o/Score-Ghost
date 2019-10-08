from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import requests
from backend import data
import urllib.parse
import time


SAVEDATA_FUNCTIONS = [
    "sv4_save_m", # Sound voltex 4
]
# Removes the server's watermark from a header value
BaseHTTPRequestHandler.server_version = ""

USER_SETTINGS = data.loadSettings()
EAMU_SERVER = USER_SETTINGS["Server_name"]
AI_MODE = USER_SETTINGS["AI_mode"]
SCOREGHOST_VER = "v1.00"

# Wait! This is hardcoded due to the services.get request, ask me on discord if you need help with another port
PROXY_SERVER = "127.0.0.1:1234"



class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def hide(self):
        self.send_response(404)
        self.end_headers()

    # Fighting to stay hidden
    def do_GET(self):
        self.hide()
    def do_PUT(self):
        self.hide()
    def do_HEAD(self):
        self.hide()
    def do_DELETE(self):
        self.hide()
    def do_PATCH(self):
        self.hide()
    def do_CRUD(self):
        self.hide()

    def do_POST(self):
        # Load contents the client sent
        contentLen = int(self.headers.get("Content-Length", 0))
        clientReq = self.rfile.read(contentLen)
        query = dict(urllib.parse.parse_qsl(self.path))
        module, method = query["module"], query["method"]

        # Create the e-amusement URL that we forward the request to
        realServerAddr = "http://%s%s"%(EAMU_SERVER, self.path)

        # Send the request to e-amusement server
        self.headers["User-Agent"] = "EAMUSE.Httpac/1.0"
        r = requests.post(realServerAddr,
                          headers=self.headers,
                          data=clientReq)

        # Send 200 statuscode and some headers to the client
        self.send_response(200)
        self.send_header("Score-Ghost", SCOREGHOST_VER)

        # Give a modified services.get so all traffic goes through this proxy
        if self.path.endswith("module=services&method=get"):
            with open("backend/files/services-get.txt","rb") as services:
                services = services.read()
            r.headers["X-Eamuse-Info"] = "1-cd382244-778c"
            r.headers["X-Compress"] = "none"
            response = services
        else:
            response = r.content

        # Send all headers from that e-amusement server response, then send content to client
        [self.send_header(key, r.headers[key]) for key in r.headers]
        self.end_headers()
        self.wfile.write(response)

        # Checking if the current request is a save request
        if method == "sv4_save_m" or AI_MODE and "save" in method:
            filename = "%s.%s_%s_%s.xml"%(module, method,
                                      self.headers.get("X-Eamuse-Info", "None"),
                                      str(int(time.time())))
            data.saveFile(data=r.content,
                          filename=filename)
            print("Saved %s.%s"%(module,method))
        else:
            print("%s.%s"%(module,method))

def startServer():
    httpd = HTTPServer(("", 1234), Handler)
    print("Score Ghost is hosted at %s \nand forwarding traffic to %s"%(PROXY_SERVER, EAMU_SERVER))
    httpd.serve_forever()
startServer()