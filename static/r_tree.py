import itertools
import math
import numpy as np
import pickle


# 最小外接矩形を求める
def joint_mbr(*points):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    return np.array([[min(x), min(y)], [max(x), max(y)]])


# 矩形間の距離を求める
def reqs_distance(req1, req2):
    c1 = np.array((req1[0] - req1[1]) / 2)
    c2 = np.array((req2[0] - req2[1]) / 2)
    return np.linalg.norm(c1 - c2, ord=2)


# 最小のペアを求める
def min_pair(data, keyfunc):
    comb = list(itertools.combinations(enumerate(data), 2))
    return min(comb, key=lambda x: keyfunc(x[0][1], x[1][1]))


# aのリストからbに含まれるインデックスを除外
def list_sub(list_a, index_b):
    return {i: a for i, a in enumerate(list_a) if i not in index_b}


# 座標が入ったリストから最小のペアを選択しつづけ新たなリストを作成
# def min_matching(positions_a, keyfunc):
#     used = []
#     new_list = []
#     new_list_target = []
#     while(len(used) < len(positions_a)):
#         now_subdict = list_sub(positions_a, used)
#         item = min_pair(now_subdict.values(), keyfunc)

#         new_list.append(item)
#         used.extend([item[0][0], item[1][0])


class RTree:

    def __init__(self, table, matrix):
        super().__init__()
        self.table = table      # インデックスと緯度経度
        self.matrix = matrix    # 隣接行列
        self.create_r_tree()


    def create_r_tree(self):
        tree = []   # tree[深さ(0が最深)][ノードインデックス][指し先=0,矩形=1]

        # 葉ノードを結合する
        tree_level = []
        use_leaves = []
        for i, i_dists in enumerate(self.matrix):

            if i in tree_level:
                # 利用済みの葉ノードは除外
                continue
            indices = [(j, dist) for j, dist in enumerate(i_dists) if (dist < np.inf) and (j not in tree_level)]

            if len(indices) < 1:
                # もし結合すべき葉ノードが見つからなかったら直前のものと結合
                leaves = (*tree_level[-1][0], i)
                r = joint_mbr(*[self.table[leaf] for leaf in leaves])
                tree_level[-1] = (leaves, r)
                use_leaves.extend([i])
            else:
                # 結合先があれば結合
                index = min(indices, key=lambda x:x[1])[0]
                leaves = (i, index)
                r = joint_mbr(*[self.table[leaf] for leaf in leaves])
                tree_level.append((leaves, r))
                use_leaves.extend([i, j])
        tree.append(tree_level)

        # 枝ノード
        while len(tree[-1]) <= 1:
            last_tl = tree[-1]
            tree_level = []
            for i in range(0, len(last_tl), 2):
                if i - 1 == len(last_tl):
                    # もし結合すべきノードが見つからなかったら直前のものと結合
                    leaves = (*tree_level[-1][0], i)
                    r = joint_mbr(*tree_level[-1][1], *last_tl[i][1])
                    tree_level[-1] = (leaves, r)
                else:
                    # 結合先があれば結合
                    leaves = (i, i+1)
                    r = joint_mbr(*[self.table[leaf] for leaf in leaves])
                    tree_level.append((leaves, r))
                    use_leaves.extend([i, j])
                p1 = last_tl[i][1]
                p2 = last_tl[i+1][1]
                r = joint_mbr(p1, p2)
















