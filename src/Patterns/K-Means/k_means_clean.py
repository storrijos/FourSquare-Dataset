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
import seaborn as sb
from sklearn.preprocessing import StandardScaler

import os, sys
curent_file_abs_path = os.path.abspath(__file__)
current_dir = os.path.dirname(curent_file_abs_path) + "/../../Processing"
carpeta2_abs_path = os.path.abspath(current_dir)
sys.path.insert(0,carpeta2_abs_path)
from pre_process import ProcessData

def findNumberClusters(data_transformed):
    Sum_of_squared_distances = []
    K = range(1, 10000, 2000)
    for k in K:
        km = KMeans(n_clusters=k)
        km = km.fit(data_transformed)
        Sum_of_squared_distances.append(km.inertia_)
        print(k)

    plt.plot(K, Sum_of_squared_distances, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Sum_of_squared_distances')
    plt.title('Elbow Method For Optimal k')
    plt.show()

def KMeanClustering(df_scaled_transformed, df):
    kmeans = sklc.KMeans(n_clusters=250, init='k-means++', random_state=42)
    k_means = kmeans.fit(df_scaled_transformed)

    cluster_map = pd.DataFrame()
    cluster_map['data_index'] = df.index.values
    cluster_map['cluster'] = k_means.labels_

    print(cluster_map[cluster_map.cluster == 3])
    return kmeans, k_means

def plot2d3dgraph(centroids_inverse, df_scaled_inverse, k_means):
    ########2D FIGURE ####
    fig = plt.figure(figsize=(15, 8))
    plt.scatter(centroids_inverse[:, 0], centroids_inverse[:, 1], s=300, c='yellow', label='Centroids')
    plt.scatter(df_scaled_inverse[:, 0], df_scaled_inverse[:, 1], c=k_means.labels_, cmap='rainbow')
    plt.xlabel('latitude')
    plt.ylabel('longitude')
    plt.legend()
    plt.show()

    ########3D FIGURE ####
    fig = plt.figure(figsize=(15, 8))
    ax = Axes3D(fig)
    ax.scatter(centroids_inverse[:, 0], centroids_inverse[:, 1], centroids_inverse[:, 2], s=300, c='yellow', label='Centroids')
    ax.scatter(df_scaled_inverse[:, 0], df_scaled_inverse[:, 1], df_scaled_inverse[:, 2], c=k_means.labels_, cmap='rainbow')
    ax.set_xlabel('latitude')
    ax.set_ylabel('longitude')
    ax.set_zlabel('timestamp')
    plt.legend()
    plt.show()



def main():
    # create blobs
    df = ProcessData.loadData('salidas/US_NewYork_POIS_Coords.txt')
    features = df.iloc[:, [2, 3, 4]].values

    df_scaled = StandardScaler().fit(features)
    df_scaled_transformed = df_scaled.transform(features)
    print(df_scaled)

    #findNumberClusters(df_scaled_transformed)

    kmeans, k_means = KMeanClustering(df_scaled_transformed, df)

    df_scaled_inverse = df_scaled.inverse_transform(df_scaled_transformed)
    centroids_inverse = df_scaled.inverse_transform(kmeans.cluster_centers_)
    print(df_scaled_inverse)

    plot2d3dgraph(centroids_inverse, df_scaled_inverse, k_means)

if __name__ == '__main__':
    main()
