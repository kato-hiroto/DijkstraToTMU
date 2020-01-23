import scipy 
import pickle

position_path_dict = pickle.load(open('./backend/position_path_dict.dump', 'rb'))
#obj = pickle.load(open('road_matrix.dump', 'rb'))
#table = obj.table

def way_to_tmu(start_id):
    return position_path_dict[start_id]
    # ここに処理を書く
    # 戻り値緯度経度のリスト
    #return [[lat, lng], [lat+0.004, lng], [lat+0.004, lng+0.004]]
