import sys
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from functools import lru_cache

# スタートを0，ゴールをNとするグラフを仮定
# ノードの数はN+1個
# ノード間には正の重みを持ったパスがあり，2つのノード間のパスは高々1本
# スタートとゴールが繋がっているときは最短経路を表示し，繋がっていない時はエラーを表示する

N = 7

# 存在するパス
# [始点, 終点, 重み]のリストを複数定義する
paths = [
    [0, 1, 2],
    [0, 2, 5],
    [1, 3, 2],
    [1, 4, 2.5],
    [2, 4, 5],
    [3, 5, 1.5],
    [4, 5, 3],
    [2, 6, 6],
    [5, 7, 1],
    [6, 7, 4],
]


# 隣接行列を上記のようなパスのリストに変換する関数
# def matrix_to_paths(m):
#     res = []
#     for i, m_row in enumerate(m):
#         for j, m_elem in enumerate(m_row):
#             if m_elem is not float("inf"):
#                 res.append([i, j, m_elem])
#     return res


# パスのリストを隣接行列へ変換する関数
# def paths_to_matrix(p, n):
#     res = np.ones((n, n)) * float("inf")
#     for elem in p:
#         res[elem[0]][elem[1]] = elem[2]
#     return res


# グラフを表示する関数
def show_graph():
    G = nx.Graph()
    G.add_nodes_from([x for x in range(N + 1)])
    G.add_edges_from([tuple([x[0], x[1], {"label": str(x[2]), "weight": 1 / x[2]}]) for x in paths])
    edge_labels = {(x[0], x[1]):str(x[2]) for x in paths}
    pos = nx.spring_layout(G)
    nx.draw_networkx(G, pos)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.axis("off")
    plt.show()

show_graph()


# 最小の距離を入れておく配列
min_distance = [0 if i == 0 else float("inf") for i in range(N + 1)]

# 最小の距離を渡した直前のノードを保存する配列
path_from = [0 if i == 0 else -1 for i in range(N + 1)]

# 確定したフラグを入れておく配列
flags = [False for _ in range(N + 1)]


# あるノードが他のノードに対して距離の重みを与える関数
def calc_distance(index):
    global min_distance
    global path_from
    global flags

    # フラグをTrueにして探索開始
    flags[index] = True
    my_distance = min_distance[index]

    # 無向グラフの場合
    to_paths = [([p[1], p[2]] if p[0] == index else [p[0], p[2]]) for p in paths if p[0] == index or p[1] == index]
    # 有向グラフの場合
    # to_paths = [[p[1], p[2]] for p in paths if p[0] == index]

    for p in to_paths:
        d = my_distance + p[1]
        if d < min_distance[p[0]]:
            # 最小値の代入
            min_distance[p[0]] = d
            path_from[p[0]] = index


while False in flags:

    # 確定していない最小の距離を持つノードを探索
    sorted_paths = sorted([[i, d] for i, d in enumerate(min_distance) if not flags[i]], key = lambda x: x[1])
    node = sorted_paths[0][0]

    # ノードの直前ノードが-1なら，到達不可能だったことを示す
    if path_from[node] == -1:
        print("このグラフには到達不可能な場所があります．")
        print("到達不可能ノード :", str([i for i in range(N + 1) if not flags[i]]))
        exit()
    
    # そうでないなら探索
    calc_distance(node)


# 最短経路を辿る関数
@lru_cache(maxsize=2**20)
def follow_path(index):
    if index == 0:
        return "0"
    else:
        return follow_path(path_from[index]) +  " -> " + str(index)

for i in range(N + 1):
    print(follow_path(i))
