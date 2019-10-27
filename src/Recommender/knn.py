"""
This module illustrates how to retrieve the k-nearest neighbors of an item. The
same can be done for users with minor changes. There's a lot of boilerplate
because of the id conversions, but it all boils down to the use of
algo.get_neighbors().
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from surprise import Dataset, Reader
from surprise.model_selection import train_test_split
from src.Patterns.Flock.fpFlockOnline import FPFlockOnline
from src.Recommender.knn_recommender import KNNCustom
from src.Processing.pre_process import ProcessData
from src.Patterns.ST_DBSCAN.main_stdbscan import STDBscan

class KNN():
    def recommender(self, filename, k, neighbors):
        dataset = ProcessData.recommender_preprocessDataset(filename)
        #Read DATASET
        reader = Reader(line_format='user item rating', rating_scale=(1, 5))
        data = Dataset.load_from_df(dataset[['id', 'item_id', 'rating']], reader)
        #data = Dataset.load_builtin('ml-100k')
        trainset, testset = train_test_split(data, test_size=.15)
        # Use user_based true/false to switch between user-based or item-based collaborative filtering
        algo = KNNCustom(k=k, sim_options={'name': 'pearson_baseline', 'user_based': True})
        algo.fit_custom(trainset, neighbors)
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
    neighbors_classified = fp.flockFinder('Datasets/US_NewYork_POIS_Coords_short.txt', output_file)
    algo_flock = knn.recommender('Datasets/US_NewYork_POIS_Coords_short.txt', 10, neighbors_classified)
    flock_prediction = knn.recommend(algo_flock, 31, 4244)
    print(flock_prediction)

    ## ST-dbscan
    st_dbscan = STDBscan()
    neighbors = st_dbscan.execute_stdbscan('Datasets/US_NewYork_POIS_Coords_short.txt')
    algo_st_dbscan = knn.recommender('Datasets/US_NewYork_POIS_Coords_short.txt', 10, neighbors)
    st_dbscan_prediction = knn.recommend(algo_st_dbscan, 31, 4244)
    print(st_dbscan_prediction)

























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

