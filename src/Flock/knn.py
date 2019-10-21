"""
This module illustrates how to retrieve the k-nearest neighbors of an item. The
same can be done for users with minor changes. There's a lot of boilerplate
because of the id conversions, but it all boils down to the use of
algo.get_neighbors().
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import io  # needed because of weird encoding of u.item file

from surprise import Reader
from surprise import KNNWithMeans
from surprise import Dataset
from surprise import accuracy
import numpy as np
from surprise.model_selection import train_test_split

from fpFlockOnline import FPFlockOnline
import pandas as pd
class KNN_custom(object):

    def __init__(self, dataset):
        self.dataset = dataset

    def get_neighbors(self, item, k):
        mask = self.dataset.traj.apply(lambda x: str(item) in x)
        df1 = self.dataset[mask]
        string_list = list(df1.traj.drop_duplicates().values)
        result = []
        for row in string_list:
            row = row.replace("]", "")
            row = row.replace("[", "")
            result.append([int(x) for x in row.split(',')])

        result = sum(result, [])
        result = list(filter(lambda x: x != item, set(result)))
        return result[:k]


def dataset_to_list_of_lists(dataset):
    string_list = list(dataset.traj.values)
    result = []
    for row in string_list:
        row = row.replace("]", "")
        row = row.replace("[", "")
        result.append([int(x) for x in row.split(',')])
    return result

def deep_search(elem, list):

    neighbors = []
    for row in list:
        if elem in row:
            neighbors.append(row)

    flatten = sum(neighbors, [])
    return [ii for n, ii in enumerate(flatten) if ii not in flatten[:n] and ii != elem]

def clasify_neighbors(list):

    flatten_list = sum(list, [])
    dict = {}

    for elem in flatten_list:
        search = deep_search(elem, list)
        if search != None:
            dict[elem] = search
    print(dict)

def preprocessDataset(filename):
    dataset = pd.read_csv(filename, delim_whitespace=True, header=None)
    dataset.columns = ["id", "item_id", "latitude", "longitude", "real_timestamp"]
    dataset.sort_values(['id', 'real_timestamp'], ascending=[True, True], inplace=True)
    dataset['timestamp'] = dataset.groupby(['id']).cumcount()
    dataset = dataset.drop(columns=['latitude', 'longitude', 'real_timestamp'])
    dataset['rating'] = np.random.randint(0, 9, len(dataset))
    return dataset


if __name__ == '__main__':
    output_file = 'output_prueba.txt' #sys.argv[1]
    fp = FPFlockOnline(0.2,3,2)
    fp.flockFinder('Datasets/US_NewYork_POIS_Coords_short.txt', output_file)
    knn = KNN_custom(fp.df)
    clasify_neighbors(dataset_to_list_of_lists(fp.df))

    #knn.get_neighbors(31, 2)

    #Read DATASET
    dataset = preprocessDataset('Datasets/US_NewYork_POIS_Coords_short_10k.txt')
    reader = Reader(line_format='user item rating', rating_scale=(0, 9))
    print(dataset)
    data = Dataset.load_from_df(dataset[['id', 'item_id', 'rating']], reader)
    #data = Dataset.load_builtin('ml-100k')
    trainset, testset = train_test_split(data, test_size=.15)
    # Use user_based true/false to switch between user-based or item-based collaborative filtering
    algo = KNNWithMeans(k=30, sim_options={'name': 'pearson_baseline', 'user_based': True})
    algo.fit(trainset)

    # we can now query for specific predicions
    uid = str(31)  # raw user id
    iid = str(3493080)  # raw item id

    # get a prediction for specific users and items.
    pred = algo.predict(uid, iid, r_ui=1, verbose=True)

    # run the trained model against the testset
    test_pred = algo.test(testset)

    #print(test_pred)

    # get RMSE
    print("User-based Model : Test Set")
    accuracy.rmse(test_pred, verbose=True)

    # if you wanted to evaluate on the trainset
    print("User-based Model : Training Set")
    train_pred = algo.test(trainset.build_testset())
    accuracy.rmse(train_pred)


