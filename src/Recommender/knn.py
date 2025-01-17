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
from src.Processing.pre_process import ProcessData
from src.Patterns.ST_DBSCAN.main_stdbscan import STDBscan
from surprise import get_dataset_dir
import io  # needed because of weird encoding of u.item file
import pandas as pd
import os
from surprise.accuracy import rmse, mae
import click
from os import path
import math
from collections import defaultdict
from surprise import SVD
from surprise import NormalPredictor
from surprise import KNNWithMeans
from surprise import NMF

def prepare_datasets(train_file, test_file):
    # TRAIN
    train_dataset = ProcessData.recommender_preprocessDataset(train_file)
    tmp_train_max = math.ceil(train_dataset['rating'].max())
    tmp_train_min = math.floor(train_dataset['rating'].min())

    reader = Reader(line_format='user item rating', rating_scale=(tmp_train_min, tmp_train_max))

    train_data = Dataset.load_from_df(train_dataset[['id', 'item_id', 'rating']], reader)
    train = train_data.construct_trainset(train_data.raw_ratings)

    # TEST
    test_dataset = ProcessData.recommender_preprocessDataset(test_file)
    test_data = Dataset.load_from_df(test_dataset[['id', 'item_id', 'rating']], reader)
    test = test_data.construct_testset(test_data.raw_ratings)

    return train, test, train_dataset, test_dataset

def precision_recall_at_k(predictions, k=10, threshold=0.5):
        '''Return precision and recall at k metrics for each user.'''

        # First map the predictions to each user.
        user_est_true = defaultdict(list)
        for uid, _, true_r, est, _ in predictions:
            user_est_true[uid].append((est, true_r))

        precisions = dict()
        recalls = dict()
        for uid, user_ratings in user_est_true.items():
            none_counter = 0
            # Sort user ratings by estimated value
            user_ratings.sort(key=lambda x: x[0], reverse=True)

            # Number of relevant items
            #n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)
            n_rel = 0
            for (_, true_r) in user_ratings:
                if true_r != None and true_r >= threshold:
                    n_rel += 1

            # Number of recommended items in top k
            sum_rek_k = 0
            for (est, rating) in user_ratings[:k]:
                if rating != None and est >= threshold:
                    sum_rek_k += 1

            # Number of relevant and recommended items in top k

            precisions[uid] = sum_rek_k / k
            # Recall@K: Proportion of relevant items that are recommended
            recalls[uid] = sum_rek_k / n_rel if n_rel != 0 else 0

        return precisions, recalls

class SVDcustom():

    def recommender_svd(self, train_file, test_file, output):

        train, test, train_dataset, test_dataset = prepare_datasets(train_file, test_file)
        # Use user_based true/false to switch between user-based or item-based collaborative filtering
        algo_svd = SVD()
        algo_svd.fit(train)

        #not_seen_elems = self.merge_train_set(train_dataset, test_dataset)

        #predictions_precision_svd = algo_svd.test(not_seen_elems, test, verbose=False, not_seen_flag=True)
        predictions_svd = algo_svd.test(test, verbose=False)

        #precisions, recalls = self.precision_recall_at_k(predictions_precision_svd, 10, threshold=0.0)
        # Precision and recall can then be averaged over all users
        #precision_avg = sum(prec for prec in precisions.values()) / len(precisions)
        #recall_avg = sum(rec for rec in recalls.values()) / len(recalls)
        #print('Precision: ' + str(precision_avg) + ' Recall: ' + str(recall_avg) + ' RMSE: ' + str(
        #    rmse(predictions_svd, verbose=False)) + ' MAE: ' + str(mae(predictions_svd, verbose=False)))
        print('SVD: ' + 'RMSE ' + str(rmse(predictions_svd, verbose=False)) + ' MAE ' + str(mae(predictions_svd, verbose=False)))

        return algo_svd

class RandomCustom():

    def recommender_random(self, train_file, test_file, output):

        train, test, train_dataset, test_dataset = prepare_datasets(train_file, test_file)
        # Use user_based true/false to switch between user-based or item-based collaborative filtering
        algo_random = NormalPredictor()

        algo_random.fit(train)

        #not_seen_elems = self.merge_train_set(train_dataset, test_dataset)

        #predictions_precision_svd = algo_svd.test(not_seen_elems, test, verbose=False, not_seen_flag=True)
        predictions_random = algo_random.test(test, verbose=False)

        #precisions, recalls = self.precision_recall_at_k(predictions_precision_svd, 10, threshold=0.0)
        # Precision and recall can then be averaged over all users
        #precision_avg = sum(prec for prec in precisions.values()) / len(precisions)
        #recall_avg = sum(rec for rec in recalls.values()) / len(recalls)
        #print('Precision: ' + str(precision_avg) + ' Recall: ' + str(recall_avg) + ' RMSE: ' + str(
        #    rmse(predictions_svd, verbose=False)) + ' MAE: ' + str(mae(predictions_svd, verbose=False)))
        print('RANDOM: ' + ' RMSE ' + str(rmse(predictions_random, verbose=False)) + ' MAE ' + str(mae(predictions_random, verbose=False)))

        return algo_random

class KNN_Baseline():

    def recommender_knn_baseline(self, train_file, test_file, output):

        train, test, train_dataset, test_dataset = prepare_datasets(train_file, test_file)
        # Use user_based true/false to switch between user-based or item-based collaborative filtering
        algo_knn_means = KNNWithMeans(verbose=False)

        algo_knn_means.fit(train)

        #not_seen_elems = self.merge_train_set(train_dataset, test_dataset)

        #predictions_precision_svd = algo_svd.test(not_seen_elems, test, verbose=False, not_seen_flag=True)
        predictions_knn_means = algo_knn_means.test(test, verbose=False)

        #precisions, recalls = self.precision_recall_at_k(predictions_precision_svd, 10, threshold=0.0)
        # Precision and recall can then be averaged over all users
        #precision_avg = sum(prec for prec in precisions.values()) / len(precisions)
        #recall_avg = sum(rec for rec in recalls.values()) / len(recalls)
        #print('Precision: ' + str(precision_avg) + ' Recall: ' + str(recall_avg) + ' RMSE: ' + str(
        #    rmse(predictions_svd, verbose=False)) + ' MAE: ' + str(mae(predictions_svd, verbose=False)))
        print('KNN_BASELINE: ' + ' RMSE ' + str(rmse(predictions_knn_means, verbose=False)) + ' MAE ' + str(mae(predictions_knn_means, verbose=False)))

        return algo_knn_means

class NMF_Baseline():

    def recommender_nmf_baseline(self, train_file, test_file, output):

        train, test, train_dataset, test_dataset = prepare_datasets(train_file, test_file)
        # Use user_based true/false to switch between user-based or item-based collaborative filtering
        algo_nmf_baseline = NMF()

        algo_nmf_baseline.fit(train)

        #not_seen_elems = self.merge_train_set(train_dataset, test_dataset)

        #predictions_precision_svd = algo_svd.test(not_seen_elems, test, verbose=False, not_seen_flag=True)
        predictions_nmf_baseline = algo_nmf_baseline.test(test, verbose=False)

        #precisions, recalls = self.precision_recall_at_k(predictions_precision_svd, 10, threshold=0.0)
        # Precision and recall can then be averaged over all users
        #precision_avg = sum(prec for prec in precisions.values()) / len(precisions)
        #recall_avg = sum(rec for rec in recalls.values()) / len(recalls)
        #print('Precision: ' + str(precision_avg) + ' Recall: ' + str(recall_avg) + ' RMSE: ' + str(
        #    rmse(predictions_svd, verbose=False)) + ' MAE: ' + str(mae(predictions_svd, verbose=False)))
        print('NMF BASELINE: ' + ' RMSE ' + str(rmse(predictions_nmf_baseline, verbose=False)) + ' MAE ' + str(mae(predictions_nmf_baseline, verbose=False)))

        return algo_nmf_baseline

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

    def get_top_n(self, predictions, n=10):
        '''Return the top-N recommendation for each user from a set of predictions.

        Args:
            predictions(list of Prediction objects): The list of predictions, as
                returned by the test method of an algorithm.
            n(int): The number of recommendation to output for each user. Default
                is 10.

        Returns:
        A dict where keys are user (raw) ids and values are lists of tuples:
            [(raw item id, rating estimation), ...] of size n.
        '''

        # First map the predictions to each user.
        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_n[uid].append((iid, est))

        # Then sort the predictions for each user and retrieve the k highest ones.
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n

    def merge_train_set(self, train, test):
        train.drop(columns=['rating'])
        test.drop(columns=['rating'])

        df_row_reindex = pd.concat([train, test], ignore_index=True)

        values = df_row_reindex.groupby('id')['item_id'].apply(lambda g: g.values.tolist()).to_dict()

        all_items = list(dict.fromkeys(df_row_reindex['item_id'].tolist()))

        items_user_not_seen = []

        for user_id, user_items_list in values.items():
            for elem_list in all_items:
                tuple_elem = (user_id, elem_list)
                items_user_not_seen.append(tuple_elem)
        return items_user_not_seen


    def recommender_knn(self, train_file, test_file, k, neighbors, output_file):

        train, test, train_dataset, test_dataset = prepare_datasets(train_file, test_file)
        # Use user_based true/false to switch between user-based or item-based collaborative filtering
        algo_knn = KNNCustom(k=k, sim_options={'name': 'pearson_baseline', 'user_based': True})
        algo_knn.fit_custom(train, neighbors)

        not_seen_elems = self.merge_train_set(train_dataset, test_dataset)

        #predictions_precision_knn = algo_knn.test(not_seen_elems, test, verbose=False, not_seen_flag=True)
        predictions_knn = algo_knn.test(not_seen_elems, test, verbose=False, not_seen_flag=False)


        top_n = self.get_top_n(predictions_knn, n=k)
        # Print the recommended items for each user
        print('TOP')
        for uid, user_ratings in top_n.items():
            for (iid, rating) in user_ratings:
                print(uid, iid, rating)
                pass

        '''
        precisions, recalls = precision_recall_at_k(predictions_precision_knn, 10, threshold=0.0)
        # Precision and recall can then be averaged over all users
        precision_avg = sum(prec for prec in precisions.values()) / len(precisions)
        recall_avg = sum(rec for rec in recalls.values()) / len(recalls)
        print('Precision: ' + str(precision_avg) + ' Recall: ' + str(recall_avg) + ' RMSE: ' + str(rmse(predictions_knn, verbose=False)) + ' MAE: ' + str(mae(predictions_knn, verbose=False)))
        '''
        return algo_knn

    def recommend(self, algo, uid, iid):
        # we can now query for specific predicions
        #uid = 31  # raw user id
        #iid = 4244  # raw item id
        #print('Prediction')
        # get a prediction for specific users and items.
        return algo.predict(uid, iid, r_ui=1, verbose=False)

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
@click.option('--pruebas', default='0', help='ejecutar pruebas con todos recomendadores')

def knn(train_file, test_file, k, neighbors_classified, uid, iid, output_file, pruebas):
    if path.exists(output_file):
        print('El fichero ' + str(output_file) + ' ya existe')
        return

    if pruebas == '1':
        svd = SVDcustom()
        algo_svd = svd.recommender_svd(train_file, test_file, output_file)

        random = RandomCustom()
        algo_random = random.recommender_random(train_file, test_file, output_file)

        knn_baseline = KNN_Baseline()
        algo_knn_baseline = knn_baseline.recommender_knn_baseline(train_file, test_file, output_file)

        nmf_baseline = NMF_Baseline()
        algo_nmf_baseline = nmf_baseline.recommender_nmf_baseline(train_file, test_file, output_file)
        return

    knn = KNN()
    neighbors_classified = knn.prepareCSV(neighbors_classified)
    algo = knn.recommender_knn(train_file,test_file,k, neighbors_classified, output_file)

    if -1 not in (uid, iid):
        prediction = knn.recommend(algo, uid, iid)

if __name__ == '__main__':
    knn()