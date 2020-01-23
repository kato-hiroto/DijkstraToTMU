import itertools
import math
import numpy as np
import pickle

from road_to_matrix import RoadMatrix


MATRIX_NAME = "./road_matrix.dump"
RTREE_NAME = "./rtree.dump"
POINT_RANGE = 0.0005


def save_pickle(obj, path):
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def read_pickle(path):
    dump = None
    with open(path, "rb") as f:
        dump = pickle.load(f)
    return dump


# リストについて
# 空リスト [] == False


# 各ノードに保存されている情報
class NodeInformation:

    def __init__(self, *, index, lat=None, lon=None, node_a=None, node_b=None, children_a=None):

        # 一時変数定義
        min_lat = None
        min_lon = None
        max_lat = None
        max_lon = None
        c = []

        # 引数の条件分岐
        if None in [node_a, node_b]:
            min_lat = lat - POINT_RANGE
            min_lon = lon - POINT_RANGE
            max_lat = lat + POINT_RANGE
            max_lon = lon + POINT_RANGE
        else:
            if lat is None:
                lat = (node_a.min_latlon[0] + node_b.min_latlon[0]) / 2
            if lon is None:
                lon = (node_a.min_latlon[1] + node_b.min_latlon[1]) / 2
            min_lat = min(node_a.min_latlon[0], node_b.min_latlon[0])
            min_lon = min(node_a.min_latlon[1], node_b.min_latlon[1])
            max_lat = max(node_a.max_latlon[0], node_b.max_latlon[0])
            max_lon = max(node_a.max_latlon[1], node_b.max_latlon[1])
            if children_a is None:
                c = [node_a.index, node_b.index]
            else:
                c.extend(children_a)
                c.append(node_b.index)
        
        # メンバ定義
        self.index = index
        self.children = c
        self.link_to = []
        self.point = np.array([lat, lon])
        self.min_latlon = np.array([min_lat, min_lon])
        self.max_latlon = np.array([max_lat, max_lon])

        
    # 隣接行列を見てリンクを持つ他ノードのインデックスを挿入
    def add_link(self, matrix):
        self.link_to = [(i, dist) for i, dist in enumerate(matrix[self.index]) if dist < np.inf]


    # 候補から最短のノードを求める
    def find_nearest(self, node_list, inventory):
        # 候補がなかった場合の値
        min_index = -1
        min_val = np.inf
        if self.link_to:
            # リンクがある場合
            cand = [(i, dist) for i, dist in self.link_to if i in inventory]
            if cand:
                return min(cand, key=lambda x:x[1])[0]
        else:
            # リンクがない場合
            for i, node_b in enumerate(node_list):
                if i not in inventory:
                    continue
                val = sum((self.point - node_b.point) ** 2)
                if val < min_val:
                    min_index = i
                    min_val = val
        return min_index


    # 指定された点を含むか
    def find(self, lat, lon):
        # flag = self.min_latlon[0] < lat and lat < self.max_latlon[0] and self.min_latlon[1] < lon and lon < self.max_latlon[1]
        # if flag:
        #     print(self.min_latlon, self.max_latlon, self.children)
        return self.min_latlon[0] < lat and lat < self.max_latlon[0] and self.min_latlon[1] < lon and lon < self.max_latlon[1]


# RTreeを内包するクラス
class RTree:

    def __init__(self, table, matrix):
        super().__init__()
        self.table = table      # インデックスと緯度経度
        self.matrix = matrix    # 隣接行列
        self.tree = []          # ここにツリー構造が入る
        self.leaves = []
        self.create_leaves()
        self.create_r_tree()


    # 葉を構成する
    def create_leaves(self):
        leaves = [NodeInformation(index=i, lat=t[0], lon=t[1]) for i, t in self.table.items()]
        for node in leaves:
            node.add_link(self.matrix)
        self.leaves = leaves


    # 木を構成する
    def create_r_tree(self):
        tree = [self.leaves]       # tree[深さ(0が最深)][ノードインデックス]

        # ノードを結合
        height = 0
        width = len(tree[height])
        while width > 1:
            level = []  # ここに結合したノードを格納
            inventory = list(range(width))
            for i, node in enumerate(tree[height]):
                if i not in inventory:
                    continue
                inventory.remove(i)
                hit = node.find_nearest(tree[height], inventory)
                if hit < 0:
                    # 該当なしなら直前に生成したノードへ結合
                    index = len(level) - 1
                    new_node = NodeInformation(index=index, node_a=level[-1], node_b=node, children_a=level[-1].children)
                    level[-1] = new_node
                else:
                    # 該当したなら見つけたノードと結合
                    index = len(level)
                    new_node = NodeInformation(index=index, node_a=node, node_b=tree[height][hit])
                    level.append(new_node)
                    inventory.remove(hit)
            tree.append(level)
            height += 1
            width = len(tree[height])

        # 木を定義
        self.tree = tree


    # 指定したノード内にある葉ノードを再帰的にすべて探索する
    def get_contain_leaves(self, lat, lon, height, index):
        node = self.tree[height][index]
        if height <= 0:
            # 葉ノードが指定されたらそのまま返す
            return [node]
        else:
            # 子ノードがあるなら探索
            in_ans = []
            out_ans = []
            in_flag = False
            for c in node.children:
                # 子ノードの内部に含まれるか
                if self.tree[height - 1][c].find(lat, lon):
                    in_ans.extend(self.get_contain_leaves(lat, lon, height - 1, c))
                    in_flag = True
                else:
                    out_ans.extend(self.get_contain_leaves(lat, lon, height - 1, c))
            if in_flag:
                # 含んでいる子ノードがあるならそれらの答えを返す
                return in_ans
            else:
                return out_ans


    # 最も近い葉ノードを探す
    def search(self, lat, lon):
        latlon = np.array([lat, lon])
        cand = self.get_contain_leaves(lat, lon, len(self.tree) - 1, 0)
        print("探索数 :", len(cand))
        cand_dists = [(c, sum((c.point - latlon) ** 2)) for c in cand]
        return min(cand_dists, key=lambda x: x[1])[0]


    # テスト用 全探索解
    def test_search(self, lat, lon):
        latlon = np.array([lat, lon])
        cand_dists = [(c, sum((c.point - latlon) ** 2)) for c in self.leaves]
        return min(cand_dists, key=lambda x: x[1])[0]


if __name__ == "__main__":
    # dump = read_pickle(MATRIX_NAME)
    # rtree = RTree(dump.table, dump.matrix)
    # save_pickle(rtree, RTREE_NAME)
    rtree = read_pickle(RTREE_NAME)
    x = float(input("lat:"))
    y = float(input("lon:"))
    node = rtree.search(x, y)
    print("latitude:", node.point[0], "longitude:", node.point[1], "distance:", np.linalg.norm(node.point - np.array([x, y]), 2))
    # print("test...")
    # node2 = rtree.test_search(x, y)
    # print("latitude:", node2.point[0], "longitude:", node2.point[1], "distance:", np.linalg.norm(node2.point - np.array([x, y]), 2))
