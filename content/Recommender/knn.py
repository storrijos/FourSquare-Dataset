"""
This module illustrates how to retrieve the k-nearest neighbors of an item. The
same can be done for users with minor changes. There's a lot of boilerplate
because of the id conversions, but it all boils down to the use of
algo.get_neighbors().
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import io  # needed because of weird encoding of u.item file

from surprise import Reader, KNNBaseline
from surprise import KNNWithMeans
from surprise import Dataset
from surprise import accuracy
import numpy as np
from surprise.model_selection import train_test_split

import os, sys
curent_file_abs_path = os.path.abspath(__file__)
current_dir = os.path.dirname(curent_file_abs_path) + "/../Processing"
carpeta2_abs_path = os.path.abspath(current_dir)
sys.path.insert(0,carpeta2_abs_path)
from pre_process import ProcessData
curent_file_abs_path = os.path.abspath(__file__)
current_dir = os.path.dirname(curent_file_abs_path) + "/../Patterns/Flock"
carpeta2_abs_path = os.path.abspath(current_dir)
sys.path.insert(0,carpeta2_abs_path)
from fpFlockOnline import FPFlockOnline
import pandas as pd

from knn_recommender import KNNCustom

if __name__ == '__main__':
    output_file = 'output_prueba.txt' #sys.argv[1]
    fp = FPFlockOnline(0.2,3,2)
    fp.flockFinder('Datasets/US_NewYork_POIS_Coords_short.txt', output_file)
    #clasify_neighbors(dataset_to_list_of_lists(fp.df))

    #knn.get_neighbors(31, 2)

    #Read DATASET
    dataset = ProcessData.recommender_preprocessDataset('Datasets/US_NewYork_POIS_Coords_short.txt')
    reader = Reader(line_format='user item rating', rating_scale=(1, 5))
    print(dataset)
    data = Dataset.load_from_df(dataset[['id', 'item_id', 'rating']], reader)
    #data = Dataset.load_builtin('ml-100k')
    trainset, testset = train_test_split(data, test_size=.15)
    # Use user_based true/false to switch between user-based or item-based collaborative filtering
    algo = KNNCustom(k=10, sim_options={'name': 'pearson_baseline', 'user_based': True})
    algo.fit_custom(trainset, fp.df)

    #algo = KNNBaseline(sim_options = {'name': 'pearson_baseline', 'user_based': False})
    #algo.fit(trainset)

    # we can now query for specific predicions
    uid = 31  # raw user id
    iid = 4244  # raw item id

    print('Prediction')
    # get a prediction for specific users and items.
    pred = algo.predict(uid, iid, r_ui=1, verbose=True)

"""
    # run the trained model against the testset
    test_pred = algo.test(testset)

    # get RMSE
    print("User-based Model : Test Set")
    accuracy.rmse(test_pred, verbose=True)

    # if you wanted to evaluate on the trainset
    print("User-based Model : Training Set")
    train_pred = algo.test(trainset.build_testset())
    accuracy.rmse(train_pred)
"""