# 0 - Import related libraries

import os
import math
import numpy as np
import click
import src.Utils.utils as Utils


from scipy.spatial.distance import directed_hausdorff

class TrajectorySimilarity(object):

    def prepareDataset(self, dataset):
        traj_data_dict = {}
        with open(dataset, 'r') as inf:
            traj_data_dict = eval(inf.read())
        traj_lst = []
        traj_keys = []

        for key, data_instance in traj_data_dict.items():
            traj_lst.append(np.vstack(data_instance[0]).T)
            traj_keys.append(key)

        return traj_lst, traj_keys

    # 3 - Distance matrix

    def hausdorff(u, v):
        d = max(directed_hausdorff(u, v)[0], directed_hausdorff(v, u)[0])
        return d

    def calculateSimilarity(self, k, dataset, output_file):

        traj_keys, D = self.calculateDistance(dataset)
        # Imprimimos los mejores vecinos para cada uno:
        with open(output_file, "a") as text_file:
            for i, item in enumerate(D):
                idx = np.argpartition(item, range(k))
                for neighbor in idx[:k]:
                    if neighbor != i and D[i][neighbor] != 0.0:
                        text_file.write(str(traj_keys[i]) + " " + str(traj_keys[neighbor]) + " " + str(D[i][neighbor]) + '\n')

    def calculateDistance(self, dataset):
        traj_lst, traj_keys = self.prepareDataset(dataset)
        traj_count = len(traj_lst)
        D = np.zeros((traj_count, traj_count))

        with open(dataset, 'r') as inf:
            traj_data_dict = eval(inf.read())

        counter = 0
        # This may take a while
        for i, u in enumerate(traj_keys):
            counter += 1
            Utils.progressBar(counter, len(traj_keys), bar_length=20)
            for j, v in enumerate(traj_keys[i+1:]):
                distance = 0
                for u_key, values1 in traj_data_dict[u][0].items():
                    for v_key, values2 in traj_data_dict[v][0].items():
                        distance += 1 - TrajectorySimilarity.hausdorff(np.vstack(values1).T, np.vstack(values2).T)
                #distance = TrajectorySimilarity.hausdorff(traj_lst[i], traj_lst[j])
                D[i, j] = distance
                D[j, i] = distance

        print(D)
        return traj_keys, D

@click.command()
@click.option('--dataset', default='US_NewYork_POIS_Coords_short.txt', help='Dataset.')
@click.option('--output_file', default='convoy_neighbors_classified.txt', help='Output file.')
@click.option('--k', default=10, help='K neighbors.')
def calculate_similarity(dataset, output_file, k):
    trajectory = TrajectorySimilarity()
    trajectory.calculateSimilarity(k, dataset, output_file)

if __name__ == '__main__':
    calculate_similarity()