# DBSCAN Clustering

# Importing the libraries
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler


def loadData(filename):
    data = pd.read_csv(filename, delim_whitespace=True, header=None)
    data.columns = ["user_id", "item_id", "lat", "long", "timestamp"]
    summary_stats = data.describe()
    print(summary_stats.to_string())
    return data

def main():
    # Importing the dataset
    df = loadData('salidas/US_NewYork_POIS_Coords_short.txt')
    features = df.iloc[:, [2, 3, 4]].values

    df_scaled = StandardScaler().fit(features)
    df_scaled_transformed = df_scaled.transform(features)

    # Using the elbow method to find the optimal number of clusters

    dbscan = DBSCAN(eps=3, min_samples=4)

    # Fitting the model

    model = dbscan.fit(df_scaled_transformed)
    unique_labels = np.unique(model.labels_)

    print(unique_labels)

    #identifying the points which makes up our core points
    sample_cores = np.zeros_like(unique_labels, dtype=bool)

    sample_cores[dbscan.core_sample_indices_] = True

    #Calculating the number of clusters

    n_clusters = len(set(unique_labels)) - (1 if -1 in unique_labels else 0)

    print(n_clusters)

    print(metrics.silhouette_score(df_scaled_transformed, unique_labels))

if __name__ == '__main__':
    main()
