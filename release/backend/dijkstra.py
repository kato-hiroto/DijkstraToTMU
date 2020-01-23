import scipy 
import pickle
from road_to_matrix import *


position_path_dict = pickle.load(open('position_path_dicti.dump', 'rb'))
#obj = pickle.load(open('road_matrix.dump', 'rb'))
#table = obj.table

def way_to_tmu(lat, lng):
    start_id = get_id_from_rtree(lat, lng)
    return position_path_dict[start_id]
    # ここに処理を書く
    # 戻り値緯度経度のリスト
    #return [[lat, lng], [lat+0.004, lng], [lat+0.004, lng+0.004]]
