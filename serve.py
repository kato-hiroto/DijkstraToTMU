from flask import Flask, render_template, request
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

PORT = 8080
app = Flask(__name__, template_folder="./")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/pipe")
def pipe():
    if request.environ.get("wsgi.websocket"):
        ws = request.environ["wsgi.websocket"]
        while True:
            msg = ws.receive()  # 受信
            if msg is None:
                break
            else:
                ws.send(msg)    # 送信
                pass

def serve_run():
    print(f"http://localhost:{PORT}")
    app.debug = True
    server = pywsgi.WSGIServer(("", PORT), app, handler_class=WebSocketHandler)
    server.serve_forever()

if __name__ == "__main__":
    serve_run()
    # python serve.py で起動，http://localhost:{PORT} に接続可能
