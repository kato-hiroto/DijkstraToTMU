import scipy
import pickle
from road_to_matrix import *
import numpy as np
from scipy.sparse.csgraph import shortest_path, floyd_warshall, dijkstra, bellman_ford, johnson
from scipy.sparse import csr_matrix


def get_path(start, goal, pred):
    return get_path_row(start, goal, pred[start])

def get_path_row(start, goal, pred_row):
    path = []
    i = goal
    while i != start and i >= 0:
        path.append(i)
        i = pred_row[i]
    if i < 0:
        return []
    path.append(i)
    return path[::-1]


if __name__ == "__main__":
    i_f = "road_matrix.dump"
    obj = pickle.load(open(i_f, 'rb'))
    table = obj.table
    goal_id = obj.university
    matrix = np.array(obj.matrix, dtype=float)
    
    _, path = shortest_path(matrix, method='D', return_predecessors=True)
    position_path_dict = dict()


    for i in range(len(matrix)):
        start_id = i
        path2tmu = get_path(start_id, goal_id, path)
        position_path = list()
        for ID in path2tmu:
            position_path.append(list(table[ID]))
        position_path_dict[start_id] = position_path

    pickle.dump(position_path_dict, open('position_path_dict.dump', 'wb'))
