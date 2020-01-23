import pickle

from flask import Flask, render_template, request
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

from backend.road_to_matrix import RoadMatrix
from backend.r_tree import NodeInformation, RTree


def read_pickle(path):
    dump = None
    with open(path, "rb") as f:
        dump = pickle.load(f)
    return dump


PORT = 8080
app = Flask(__name__, template_folder="./")
road_matrix = read_pickle("./backend/road_matrix.dump")
# rtree = read_pickle("./backend/r_tree.dump")
rtree = RTree(road_matrix.table, road_matrix.matrix)
position_path_dict = read_pickle('./backend/position_path_dict.dump')


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/pipe")
def pipe():
    if request.environ.get("wsgi.websocket"):
        print("open html")
        ws = request.environ["wsgi.websocket"]
        while True:
            msg = ws.receive()  # 受信
            if msg is None:break
            else:
                lat, lng = map(float, msg.split(','))
                print("receive lat:", lat, "lng:", lng)
                start_id = rtree.return_id(lat, lng)
                result = position_path_dict[start_id]
                result_json = json_dumps(result)
                print(result_json)
                ws.send(result_json)    # 送信

def json_dumps(result):
    return "{\"elements\":" + str(result) + "}"

def serve_run():
    print(f"http://localhost:{PORT}")
    app.debug = True
    server = pywsgi.WSGIServer(("", PORT), app, handler_class=WebSocketHandler)
    server.serve_forever()

if __name__ == "__main__":
    serve_run()
    # python serve.py で起動，http://localhost:{PORT} に接続可能
