from flask import Flask, render_template, request
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

PORT = 8080
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/pipe")
def pipe():
    if request.environ.get("wsgi.websocket"):
        ws = request.environ["wsgi.websocket"]
        while True:
            msg = ws.receive()
            if msg is None:
                break       # 受信情報がNoneなら接続終了
            else:
                agent.receive(msg)

def serve_run():
    print(f"http://localhost:{PORT}")
    app.debug = True
    server = pywsgi.WSGIServer(("", PORT), app, handler_class=WebSocketHandler)
    server.serve_forever()

if __name__ == "__main__":
    serve_run()
