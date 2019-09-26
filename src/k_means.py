# import KMeans
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt
import pandas as pd
import os
import sys
import json
import time
import random
import datetime
import numpy as np
import pandas as pd
import sklearn.cluster as sklc
import sklearn.metrics as sklm
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.mplot3d import Axes3D


def loadData(filename):
    data = pd.read_csv(filename, delim_whitespace=True, header=None)
    data.columns = ["user_id", "item_id", "lat", "long", "timestamp"]
    summary_stats = data.describe()
    print(summary_stats.to_string())
    return data

def main():
    # create blobs
    df = loadData('salidas/US_NewYork_POIS_Coords.txt')
    #kmeans = KMeans(n_clusters=3).fit(df)
    #centroids = kmeans.cluster_centers_
    #print(centroids)
    #plt.scatter(df['lat'], df['long'], df['timestamp'], c = kmeans.labels_.astype(float), s=50, alpha=0.5)
    #plt.scatter(centroids[:, 0], centroids[:, 1], c='red', s=50)
    #plt.show()

    df_analyzed, df_clusters = calc_kmeans(df, 11)
    df_clusters.head()
    plt.scatter(df_clusters.index, df_clusters['silhouette_score'])
    plt.show()
    plt.plot(df_clusters['sse'])
    plt.show()
    df_clusters

    centers10 = df_clusters.iloc[3]['cluster_centers'][:]
    plt.figure(figsize=(15, 8))
    # plt.subplot(211)
    plt.scatter(df_analyzed['lat'], df_analyzed['long'], c=df_analyzed['k8_labels'])
    #plt.show()
    plt.scatter(centers10[:, 0], centers10[:, 1], marker='+', s=1000)
    plt.show()
    plt.hist(df_analyzed[df_analyzed['k8_labels'] == 1]['timestamp'])
    plt.show()
    print(df_analyzed.describe())
    print(df_clusters.describe())
    print('EL NORMAL')
    print(df.describe().to_string())

    plt.figure(figsize=(15, 20))
    plt.subplot(211)
    plt.scatter(df['lat'], df['long'], c=df['k8_labels'])
    plt.show()
    #plt.subplot(212)
    #plt.scatter(df['timestamp'], df['fatalities'], c=df['k4_labels'])

    # plt.subplot(212)
    # plt.scatter(df_analyzed['event_datetime_norm'], df_analyzed['latitude'], c=df_analyzed['k11_labels'])


def calc_kmeans(df, rangek):
    start = time.time()
    if type(rangek) is int:
        rangek = range(2, rangek + 1, 3)

    df_tmp = df[["lat", "long", "timestamp"]]
    clusters = []
    for k in rangek:
        ktmp = sklc.KMeans(n_clusters=k).fit(df_tmp)
        silhouette_tmp = sklm.silhouette_score(df_tmp, ktmp.labels_)

        df['k' + str(k) + '_labels'] = ktmp.labels_
        clusters.append([k, ktmp.cluster_centers_, ktmp.inertia_, silhouette_tmp])
        print (k, 'out of', rangek, 'clusters analyzed.')

    df_clusters = pd.DataFrame(clusters, columns=['k', 'cluster_centers', 'sse', 'silhouette_score']).set_index('k')
    end = time.time()
    print('Analyzing', str(max(rangek)), ' values of k took', end - start, 'seconds for this data with', len(df_tmp),
          'observations.')
    return df.drop_duplicates(), df_clusters
if __name__ == '__main__':
    main()
