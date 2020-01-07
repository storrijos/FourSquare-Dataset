# 0 - Import related libraries

import numpy as np
import click
import src.Utils.utils as Utils
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import directed_hausdorff
from math import sin, cos, sqrt, atan2, radians
import os.path
from multiprocessing import Pool, Process, Value, Manager, Array, cpu_count, Lock
from functools import partial
import copy
from os import path
import ctypes as c
import json

class TrajectorySimilarity(object):

    def prepareDataset(self, dataset):
        traj_data_dict = {}
        with open(dataset, 'r') as inf:
            traj_data_dict = json.loads(inf.read())

        traj_lst = []
        traj_keys = []

        for key, data_instance in traj_data_dict.items():
            traj_lst.append(np.vstack(data_instance[0]).T)
            traj_keys.append(key)

        return traj_lst, traj_keys

    # 3 - Distance matrix
    def removeNaN(self, list):
        total_arr = []
        for elems in list:
            elem = elems[np.logical_not(np.isnan(elems))]
            if elem.size > 0:
                total_arr.append(elem.tolist())
        return total_arr

    def similarity_function(self, v, function, u):
        #v = np.vstack(v).T
        u = self.removeNaN(u)
        v = self.removeNaN(v)

        #u = u[np.logical_not(np.isnan(u))]

        if function == 'hausdorff':
            return 1 - TrajectorySimilarity.hausdorff(u, v)
        elif function == 'dtw':
            return 1 - TrajectorySimilarity.dtw(u, v)
        elif function == 'lcss':
            pass
        else:
            return 1 - TrajectorySimilarity.hausdorff(u, v)

    def dtw(u, v):
        distance, path = fastdtw(u, v, dist=euclidean)
        return distance

    def hausdorff(u, v):
        d = max(directed_hausdorff(u, v)[0], directed_hausdorff(v, u)[0])
        return d

    def calculateSimilarity(self, k, dataset, output_file, function):
        traj_keys, D = self.calculateDistance(dataset, function)
        # Imprimimos los mejores vecinos para cada uno:

        if path.exists(output_file):
            print('El fichero' + str(output_file) + 'ya existe')
        else:
            with open(output_file, "a") as text_file:
                for i, item in enumerate(D):
                    if k > len(item):
                        k = len(item)
                    idx = np.argpartition(item, range(k))
                    for neighbor in idx[:k]:
                        if neighbor != i and D[i][neighbor] != 0.0:
                            text_file.write(str(traj_keys[i]) + " " + str(traj_keys[neighbor]) + " " + str(D[i][neighbor]) + '\n')

#    def update_dist(self, function, traj_data_dict, u, v, x, i, j, traj_keys):

    def update_dist(self, function, traj_data_dict, u, x, i, traj_keys):
        for j, v in enumerate(traj_keys[i + 1:], start=i + 1):
            if j >= len(traj_keys):
                break

            distance = 0
            for u_key, values1 in traj_data_dict[u][0].items():
                for v_key, values2 in traj_data_dict[v][0].items():
                    distance += self.similarity_function(np.vstack(values1).T, function, np.vstack(values2).T)

            D[i][j] = distance
            D[j][i] = distance

        global count
        with count.get_lock():
            count.value += 1
            print(str(count.value) + "/" + str(len(traj_keys)))
        print("DONE: " + str(i) + "\n")

    def calculateDistance(self, dataset, function):
        traj_lst, traj_keys = self.prepareDataset(dataset)
        traj_count = len(traj_lst)
        #D = np.zeros((traj_count, traj_count))

        arr = Array(c.c_double, traj_count * traj_count)
        arr = np.frombuffer(arr.get_obj())
        global D
        D = arr.reshape((traj_count, traj_count))
        global count
        count = Value('i', 0)

        with open(dataset, 'r') as inf:
            traj_data_dict = json.loads(inf.read())
            #traj_data_dict = eval(inf.read())

        counter = 0
        sub_counter = 0
        nprocs = cpu_count() - 1
        pool = Pool(processes=nprocs)

        for i, u in enumerate(traj_keys):
            #counter += 1
            #print(str(counter) + " " + str(len(traj_keys)) + "\n")
            #Utils.progressBar(counter, len(traj_keys), bar_length=20)
            sub_counter = 0
            pool.apply_async(self.update_dist, args=(function, traj_data_dict, u, [], i, traj_keys))

            '''
            #for j, v in enumerate(traj_keys[i+1:], start=i+1):
             #   if j >= len(traj_keys):
              #      break
               # sub_counter += 1
                #distance = 0
                #print(sub_counter, len(traj_keys[i+1:]))
                #value = []
                #print(i,j)
               # prod_x = partial(self.update_dist, traj_data_dict=traj_data_dict, function=function, u=u, v=v, x=[], i=i, j=j)
                #pool.apply_async(self.update_dist, args=(function, traj_data_dict, u, v, [], i, j))
                #pool.map_async(prod_x, [1])
                #p = Process(target=prod_x)
                #proc.append(p)

                #self.update_dist(function, traj_data_dict, u, v, D, i, j)

    
                for u_key, values1 in traj_data_dict[u][0].items():
                    prod_x = partial(self.similarity_function, function=function, u=np.vstack(values1).T)
                    r = p.map_async(prod_x, traj_data_dict[v][0].values(), callback=value.append)
                r.wait()
                #distance += sum(result)
                #print('a')
                #print(value)
                distance += sum(sum(value, []))
                #print(distance)
                    #for v_key, values2 in traj_data_dict[v][0].items():
                     #   distance += 1 - self.similarity_function(function, np.vstack(values1).T, np.vstack(values2).T)
                        #distance += 1 - TrajectorySimilarity.hausdorff(np.vstack(values1).T, np.vstack(values2).T)
                #distance = TrajectorySimilarity.hausdorff(traj_lst[i], traj_lst[j])
                #print(i, j, distance)

                D[i, j] = distance
                D[j, i] = distance
                
                '''

        pool.close()
        pool.join()

        return traj_keys, D

@click.command()
@click.option('--dataset', default='US_NewYork_POIS_Coords_short.txt', help='Dataset.')
@click.option('--output_file', default='similarity_output_convoy.txt', help='Output file.')
@click.option('--k', default=10, help='K neighbors.')
@click.option('--function', default='dtw', help='dtw.')

def calculate_similarity(dataset, output_file, k, function):
    if path.exists(output_file):
        print('El fichero ' + str(output_file) + ' ya existe')
        return

    trajectory = TrajectorySimilarity()
    trajectory.calculateSimilarity(k, dataset, output_file, function)

if __name__ == '__main__':
    calculate_similarity()
