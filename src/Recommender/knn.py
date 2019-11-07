"""
This module illustrates how to retrieve the k-nearest neighbors of an item. The
same can be done for users with minor changes. There's a lot of boilerplate
because of the id conversions, but it all boils down to the use of
algo.get_neighbors().
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from surprise import Dataset, Reader, Trainset
from surprise.model_selection import train_test_split
from src.Patterns.Flock.fpFlockOnline import FPFlockOnline
from src.Recommender.knn_recommender import KNNCustom
from src.Processing.pre_process import ProcessData, find_path
from src.Patterns.ST_DBSCAN.main_stdbscan import STDBscan
import pandas as pd
import os

class KNN():

    def recommender(self, train_file, test_file, k, neighbors):
        reader = Reader(line_format='user item rating', rating_scale=(1, 5))

        #TRAIN
        train_dataset = ProcessData.recommender_preprocessDataset(train_file)
        train_data = Dataset.load_from_df(train_dataset[['id', 'item_id', 'rating']], reader)
        train = train_data.construct_trainset(train_data.raw_ratings)

        #TEST
        test_dataset = ProcessData.recommender_preprocessDataset(test_file)
        test_data = Dataset.load_from_df(test_dataset[['id', 'item_id', 'rating']], reader)
        test = test_data.construct_testset(test_data.raw_ratings)

        # Use user_based true/false to switch between user-based or item-based collaborative filtering
        algo = KNNCustom(k=k, sim_options={'name': 'pearson_baseline', 'user_based': True})

        algo.fit_custom(train, neighbors)
        return algo

    def recommend(self, algo, uid, iid):
        # we can now query for specific predicions
        #uid = 31  # raw user id
        #iid = 4244  # raw item id
        print('Prediction')
        # get a prediction for specific users and items.
        return algo.predict(uid, iid, r_ui=1, verbose=True)

if __name__ == '__main__':
    knn = KNN()
    ###FLOCK
    output_file = 'output_prueba.txt' #sys.argv[1]
    fp = FPFlockOnline(0.2,3,2)
    curent_file_abs_path = os.path.dirname(os.path.realpath(__file__))
    fp.flockFinder('Datasets/US_NewYork_POIS_Coords_short.txt', output_file)

    flock_neighbors_path = str(curent_file_abs_path) + '/flock_neighbors_classified.txt'
    if os.path.exists(flock_neighbors_path):
        flock_neighbors_classified = pd.read_csv(flock_neighbors_path, delim_whitespace=True, header=None)
        flock_neighbors_classified.columns = ["user_id", "neighbour_id", "weight"]

        algo_flock = knn.recommender('Datasets/US_NewYork_POIS_Coords_short.txt',
                                     'Datasets/US_NewYork_POIS_Coords_short.txt',
                                     10, flock_neighbors_classified)
        flock_prediction = knn.recommend(algo_flock, 31, 4244)

    ## ST-dbscan
    st_dbscan = STDBscan()
    st_dbscan.execute_stdbscan('Datasets/US_NewYork_POIS_Coords_short_1k.txt')
    st_dbscan_neighbors_path = str(curent_file_abs_path) + '/st_dbscan_neighbors_classified.txt'
    if os.path.exists(st_dbscan_neighbors_path):
        st_dbscan_neighbors_classified = pd.read_csv(str(curent_file_abs_path) + '/st_dbscan_neighbors_classified.txt',
                                                     delim_whitespace=True, header=None)
        st_dbscan_neighbors_classified.columns = ["user_id", "neighbour_id", "weight"]
        algo_st_dbscan = knn.recommender('Datasets/US_NewYork_POIS_Coords_short.txt',
                                         'Datasets/US_NewYork_POIS_Coords_short.txt',
                                         10, st_dbscan_neighbors_classified)
        st_dbscan_prediction = knn.recommend(algo_st_dbscan, 31, 4244)

























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

