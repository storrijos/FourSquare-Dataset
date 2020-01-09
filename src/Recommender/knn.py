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
from src_rec.Patterns.Flock.fpFlockOnline import FPFlockOnline
from src_rec.Recommender.knn_recommender import KNNCustom
from src_rec.Processing.pre_process import ProcessData
from src_rec.Patterns.ST_DBSCAN.main_stdbscan import STDBscan
from surprise import get_dataset_dir
import io  # needed because of weird encoding of u.item file
import pandas as pd
import os
from surprise.accuracy import rmse
import click
from os import path
import math

class KNN():


    def __init__(self):
        self.trainset = []

    def read_item_names(self, file_name):
        """Read the u.item file from MovieLens 100-k dataset and return two
        mappings to convert raw ids into movie names and movie names into raw ids.
        """
        rid_to_name = {}
        name_to_rid = {}
        with io.open(file_name, 'r', encoding='ISO-8859-1') as f:
            for line in f:
                line = line.split('|')
                rid_to_name[line[0]] = line[1]
                name_to_rid[line[1]] = line[0]

        return rid_to_name, name_to_rid

    # Let's build a pandas dataframe with all the predictions

    def get_Iu(self, uid):
        """Return the number of items rated by given user

        Args:
            uid: The raw id of the user.
        Returns:
            The number of items rated by the user.
        """

        try:
            return len(self.trainset.ur[self.trainset.to_inner_uid(uid)])
        except ValueError:  # user was not part of the trainset
            return 0

    def get_Ui(self, iid):
        """Return the number of users that have rated given item

        Args:
            iid: The raw id of the item.
        Returns:
            The number of users that have rated the item.
        """

        try:
            return len(self.trainset.ir[self.trainset.to_inner_iid(iid)])
        except ValueError:  # item was not part of the trainset
            return 0

    def recommender(self, train_file, test_file, k, neighbors, output_file):

        #TRAIN
        train_dataset = ProcessData.recommender_preprocessDataset(train_file)
        tmp_train_max = math.ceil(train_dataset['rating'].max())
        tmp_train_min = math.floor(train_dataset['rating'].min())

        reader = Reader(line_format='user item rating', rating_scale=(tmp_train_min, tmp_train_max))

        train_data = Dataset.load_from_df(train_dataset[['id', 'item_id', 'rating']], reader)
        train = train_data.construct_trainset(train_data.raw_ratings)

        #TEST
        test_dataset = ProcessData.recommender_preprocessDataset(test_file)
        test_data = Dataset.load_from_df(test_dataset[['id', 'item_id', 'rating']], reader)
        test = test_data.construct_testset(test_data.raw_ratings)

        # Use user_based true/false to switch between user-based or item-based collaborative filtering
        algo = KNNCustom(k=k, sim_options={'name': 'pearson_baseline', 'user_based': True})

        algo.fit_custom(train, neighbors)
        #print('test')
        #print(test)
        predictions = algo.test(test)
        rmse(predictions)

        #print('TRAINSET2')
        self.trainset = algo.trainset
        print('algo: {0}, k = {1}, min_k = {2}'.format(algo.__class__.__name__, algo.k, algo.min_k))

        df = pd.DataFrame(predictions, columns=['uid', 'iid', 'rui', 'est', 'details'])
        df['Iu'] = df.uid.apply(self.get_Iu)
        df['Ui'] = df.iid.apply(self.get_Ui)
        df['err'] = abs(df.est - df.rui)

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', -1)

        #'RESULTS'
        df.to_csv(output_file, sep=' ')

        return algo

    def recommend(self, algo, uid, iid):
        # we can now query for specific predicions
        #uid = 31  # raw user id
        #iid = 4244  # raw item id
        print('Prediction')
        # get a prediction for specific users and items.
        return algo.predict(uid, iid, r_ui=1, verbose=True)

    def prepareCSV(self, filename):
        neighbors_classified = pd.read_csv(filename, delim_whitespace=True, header=None)
        neighbors_classified.columns = ["user_id", "neighbour_id", "weight"]
        return neighbors_classified

@click.command()
@click.option('--train_file', default='US_NewYork_POIS_Coords_short.txt', help='Dataset.')
@click.option('--test_file', default='US_NewYork_POIS_Coords_short.txt', help='Dataset.')
@click.option('--k', default=2, help='Min k neighbors.')
@click.option('--neighbors_classified', default='similarity_output_convoy.txt', help='Output file.')
@click.option('--uid', default=-1, help='user id')
@click.option('--iid', default=-1, help='item id.')
@click.option('--output_file', default='knn_output.txt', help='output_file')


def knn(train_file, test_file, k, neighbors_classified, uid, iid, output_file):
    if path.exists(output_file):
        print('El fichero ' + str(output_file) + ' ya existe')
        return

    knn = KNN()
    neighbors_classified = knn.prepareCSV(neighbors_classified)
    algo = knn.recommender(train_file,test_file,k, neighbors_classified, output_file)

    if -1 not in (uid, iid):
        prediction = knn.recommend(algo, uid, iid)

if __name__ == '__main__':
    knn()
    """
    knn = KNN()
    ###FLOCK
    output_file = 'output_prueba.txt' #sys.argv[1]
    fp = FPFlockOnline(0.2,3,2)
    curent_file_abs_path = os.path.dirname(os.path.realpath(__file__))
    fp.flockFinder('Datasets/US_NewYork_POIS_Coords_short.txt', output_file)

    flock_neighbors_path = str(curent_file_abs_path) + '/flock_neighbors_classified.txt'
    if os.path.exists(flock_neighbors_path):
        flock_neighbors_classified = knn.prepareCSV(flock_neighbors_path)
        algo_flock = knn.recommender('Datasets/US_NewYork_POIS_Coords_short.txt',
                                     'Datasets/US_NewYork_POIS_Coords_short_test.txt',
                                     1, flock_neighbors_classified)
        flock_prediction = knn.recommend(algo_flock, 15, 6589)

    ## ST-dbscan
    st_dbscan = STDBscan()
    st_dbscan.execute_stdbscan('Datasets/US_NewYork_POIS_Coords_short_1k.txt')
    st_dbscan_neighbors_path = str(curent_file_abs_path) + '/st_dbscan_neighbors_classified.txt'
    if os.path.exists(st_dbscan_neighbors_path):
        st_dbscan_neighbors_classified = knn.prepareCSV(st_dbscan_neighbors_path)
        algo_st_dbscan = knn.recommender('Datasets/US_NewYork_POIS_Coords_short.txt',
                                         'Datasets/US_NewYork_POIS_Coords_short.txt',
                                         10, st_dbscan_neighbors_classified)
        st_dbscan_prediction = knn.recommend(algo_st_dbscan, 31, 4244)
    """
























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
