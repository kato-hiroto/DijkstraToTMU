import itertools
import math
import numpy as np
import pickle

from .road_to_matrix import RoadMatrix


DUMP_NAME = "./static/road_matrix.dump"


def read_pickle(path):
    dump = None
    with open(path, "rb") as f:
        dump = pickle.load(f)
    return dump


# 最小外接矩形を求める
def joint_mbr(*points):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    return np.array([[min(x), min(y)], [max(x), max(y)]])


# 矩形間の距離を求める
def reqs_distance(req1, req2):
    c1 = (req1[0] - req1[1]) / 2
    c2 = (req2[0] - req2[1]) / 2
    return np.linalg.norm(c1 - c2, ord=2)


# 最小のペアを求める
def min_pair(enumdata, keyfunc, count):
    comb = list(itertools.combinations(enumdata, 2))
    return min(comb, key=lambda x: keyfunc(x[0][1], x[1][1]))


def min_pair_first(enumdata, table, matrix):
    i = enumdata[0][0]
    indices = [(j, matrix[i, j[0]] for j in enumdata if matrix[i, j[0]] < np.inf]
    index = min(indices, key=lambda x:x[1])[0]
    return ((i, table[i]), (j, table[j]))


# aのリストからbに含まれるインデックスを除外
def list_sub(list_a, index_b, count):
    return [(i, a) for i, a in enumerate(list_a) if i not in index_b]


# 座標が入ったリストから最小のペアを選択しつづけ新たなリストを作成
def min_matching(positions, sizefunc, margefunc):
    used = []
    new_list = []
    new_list_target = []

    count = 0
    while len(positions) - len(used) > 1:
        sub = list_sub(positions, used)
        item = min_pair(sub, sizefunc)
        used.extend([item[0][0], item[1][0]])
        new_list.append((item[0][1], item[1][1]))
        new_list_target.append((item[0][0], item[1][0]))
        count += 1
        if count % 100 == 0:
            print(used)

    if len(positions) - len(used) == 1:
        sub = list_sub(positions, used, 0)
        tmp = new_list[-1]
        new_list[-1] = margefunc(*tmp, sub[0][1])
        new_list_target[-1].append(sub[0][0])
    return new_list, new_list_target


class RTree:

    def __init__(self, table, matrix):
        super().__init__()
        self.table = table      # インデックスと緯度経度
        self.matrix = matrix    # 隣接行列
        self.create_r_tree()


    def create_r_tree(self):
        tree = []       # tree[深さ(0が最深)][ノードインデックス][指し先=0,矩形=1]

        # 葉ノードを結合する
        # level[ノードインデックス][矩形=0,指し先=1]
        leaves = [i for i in range(len(self.matrix))]
        l, l_target = min_matching(leaves, sizefunc=lambda x, y: self.matrix[x, y], margefunc=lambda *x: x)
        level = [(joint_mbr(self.table[j] for j in l[i]), l_target[i]) for i in range(len(l))]
        tree.append(level)

        # 枝を順に結合する
        while len(tree[-1]) > 1:
            leaves = [leaf[0] for leaf in tree[-1]]
            l, l_target = min_matching(leaves, sizefunc=lambda x, y: reqs_distance(x, y), margefunc=joint_mbr)
            level = [(l[i], l_target[i]) for i in range(len(l))]
            tree.append(level)

        self.tree = tree
        print(tree)


if __name__ == "__main__":
    dump = read_pickle(DUMP_NAME)
    rtree = RTree(dump.table, dump.matrix)




        
        # for i, i_dists in enumerate(self.matrix):

        #     if i in tree_level:
        #         # 利用済みの葉ノードは除外
        #         continue
        #     indices = [(j, dist) for j, dist in list_sub(i_dists, use_leaves) if dist < np.inf]

        #     if len(indices) < 1:
        #         # もし結合すべき葉ノードが見つからなかったら直前のものと結合
        #         leaves = (*tree_level[-1][0], i)
        #         r = joint_mbr(*[self.table[leaf] for leaf in leaves])
        #         tree_level[-1] = (leaves, r)
        #         use_leaves.extend([i])
        #     else:
        #         # 結合先があれば結合
        #         index = min(indices, key=lambda x:x[1])[0]
        #         leaves = (i, index)
        #         r = joint_mbr(*[self.table[leaf] for leaf in leaves])
        #         tree_level.append((leaves, r))
        #         use_leaves.extend([i, j])
        # tree.append(tree_level)

        # # 枝ノード
        # while len(tree[-1]) <= 1:
        #     last_tl = tree[-1]
        #     tree_level = []
        #     for i in range(0, len(last_tl), 2):
        #         if i - 1 == len(last_tl):
        #             # もし結合すべきノードが見つからなかったら直前のものと結合
        #             leaves = (*tree_level[-1][0], i)
        #             r = joint_mbr(*tree_level[-1][1], *last_tl[i][1])
        #             tree_level[-1] = (leaves, r)
        #         else:
        #             # 結合先があれば結合
        #             leaves = (i, i+1)
        #             r = joint_mbr(*[self.table[leaf] for leaf in leaves])
        #             tree_level.append((leaves, r))
        #             use_leaves.extend([i, j])
        #         p1 = last_tl[i][1]
        #         p2 = last_tl[i+1][1]
        #         r = joint_mbr(p1, p2)
















