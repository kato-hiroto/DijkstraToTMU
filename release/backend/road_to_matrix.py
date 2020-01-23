import json
import math
import numpy as np
import pickle


PATH = "./hino_road.json"
DUMP_NAME = "road_matrix.dump"
UID_START = 0


def read_text(path):
    text = None
    with open(path, "r", encoding="utf-8_sig") as f:
        text = f.read()
    return text


def save_pickle(obj, path):
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def road_to_matrix(path):
    # 保存領域
    uid_table = {}
    point_table = {}
    adj_matrix = []

    obj = json.loads(read_text(path))
    features = obj["features"]
    uid_max = UID_START
    for f in features:

        # 道路以外は読み飛ばし
        if f["geometry"]["type"] != "LineString":
            continue

        # 各道路の処理
        prev_uid = -1
        prev_point = None
        for c in f["geometry"]["coordinates"]:

            # ポイント間の距離を測る
            c = [c[1], c[0]]
            cost = math.inf
            p = np.array(c)
            if prev_point is not None:
                cost = np.linalg.norm(p - prev_point, ord=2)
            prev_point = p

            # 隣接行列への追加
            node = str(c)
            if node not in uid_table.keys():
                # 新しく発見した点なら行を増やす
                uid = uid_max
                uid_table[node] = uid_max
                point_table[uid] = p
                adj_matrix.append([math.inf] * (prev_uid + 1))
                if prev_uid >= 0:
                    adj_matrix[uid][prev_uid] = cost
                uid_max += 1
                prev_uid = uid
            elif prev_uid >= 0:
                # 以前にもあった点なら対応する行の列を増やす
                uid = uid_table[node]
                addsize = prev_uid - len(adj_matrix[uid]) + 1
                # print("addsize :", addsize)
                if addsize > 0:
                    adj_matrix[uid].extend([math.inf] * addsize)
                adj_matrix[uid][prev_uid] = cost
                prev_uid = uid
    print("uid_max :", uid_max)

    # numpy行列への書き起こし
    np_matrix = np.ones((uid_max, uid_max)) * np.inf
    for i, r in enumerate(adj_matrix):
        for j, c in enumerate(r):
            if c < math.inf:
                np_matrix[i, j] = c
                np_matrix[j, i] = c
    
    # inf -> 0
    f = np.frompyfunc(lambda x: 0 if x == np.inf else x, 1, 1)
    np_matrix = f(np_matrix)

    # 学校のノード検索
    university = uid_table[str([35.6613086, 139.3682016])]

    return university, point_table, np_matrix


class RoadMatrix:
    def __init__(self, univ, tab, mat):
        self.university = univ
        self.table = tab
        self.matrix = mat


if __name__ == "__main__":
    univ, tab, mat = road_to_matrix(PATH)
    print(univ)
    # print("table :", tab)
    print("matrix :", mat)
    save_pickle(RoadMatrix(univ, tab, mat), DUMP_NAME)
