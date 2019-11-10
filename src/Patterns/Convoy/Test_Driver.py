from TrajectoryParser import TrajectoryParser
from CMC import CMC
from src.Processing.pre_process import ProcessData
import pandas as pd

def convoy_preprocessDataset(filename):
    dataset = pd.read_csv(filename, delim_whitespace=True, header=None)
    dataset.columns = ["obj_id", "item_id", "x", "y", "t"]
    dataset.sort_values(['obj_id', 't'], ascending=[True, True], inplace=True)
    dataset['t'] = dataset.groupby(['obj_id']).cumcount() + 1
    dataset = dataset.drop(columns=['item_id'])

    header = ["obj_id", "t", "x", "y"]
    dataset.to_csv('resource/output.csv', columns=header, index=False, sep=',')

    return dataset

if __name__ == '__main__':

    #obj_id, t, x, y

    dataset = convoy_preprocessDataset('resource/US_NewYork_POIS_Coords_short.txt')

    parser = TrajectoryParser("resource/output.csv")
    traj_set = parser.get_traj_set()

    #minPoints, #lifetime, #distance_max

    res = CMC.cm_clustering(traj_set, 10, 2, 0.005)
    print("\n")
    for conv in res:
        print(conv.toString())
