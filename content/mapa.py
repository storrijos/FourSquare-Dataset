# DBSCAN Clustering

# Importing the libraries
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
import sklearn.utils
from sklearn.preprocessing import StandardScaler

from mpl_toolkits.basemap import Basemap
import matplotlib
from PIL import Image
import matplotlib.pyplot as plt
#print (matplotlib.__version__)
from pylab import rcParams
rcParams['figure.figsize'] = (14,10)


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

    west, south, east, north = -74.02, 40.55, -73.75, 40.90

    my_map = Basemap(projection='cyl', llcrnrlat=south, urcrnrlat=north,
                llcrnrlon=west, urcrnrlon=east, lat_ts=south, resolution='l')

    my_map.drawcoastlines()
    my_map.drawcountries()
    #my_map.drawlsmask(land_color='orange', ocean_color='skyblue')
    my_map.shadedrelief()
    #my_map.bluemarble()
    # To collect data based on stations
    xs, ys = my_map(np.asarray(df['long']), np.asarray(df['lat']))
    #print(xs)
    df['xm']= xs.tolist()
    df['ym'] =ys.tolist()

    #Visualization1
    for index, row in df.iterrows():
    #   x,y = my_map(row.Long, row.Lat)
        my_map.plot(row.xm, row.ym, markerfacecolor = 'lime', markeredgecolor='pink', marker='s', markersize= 10, alpha = 0.4)
        print(row.xm)
        print(row.ym )

    #plt.text(x,y,stn)
    plt.title("User points in New York", fontsize=14)
    plt.savefig("Canada_WS.png", dpi=300)
    #plt.show()

    df_temp = df[["xm", "ym"]]
    df_temp = StandardScaler().fit_transform(df_temp)
    db = DBSCAN(eps=50000, min_samples=1).fit(df_temp)
    labels = db.labels_
    print (labels)
    df["Clus_Db"]=labels

    realClusterNum=len(set(labels)) - (1 if -1 in labels else 0)
    clusterNum = len(set(labels))

    set(labels)
    clusterMap(labels, df)


def clusterMap(labels, df):
    west, south, east, north = -74.02, 40.55, -73.75, 40.90
    clusterNum = len(set(labels))

    my_map = Basemap(projection='cyl', llcrnrlat=south, urcrnrlat=north,
                llcrnrlon=west, urcrnrlon=east, lat_ts=south, resolution='l')

    my_map.drawcoastlines()
    my_map.drawcountries()
    my_map.etopo()

    # To create a color map
    colors = plt.get_cmap('jet')(np.linspace(0.0, 1.0, clusterNum))

    # Visualization1
    for clust_number in set(labels):
        c = (([0.4, 0.4, 0.4]) if clust_number == -1 else colors[np.int(clust_number)])
        clust_set = df[df.Clus_Db == clust_number]
        my_map.scatter(clust_set.xm, clust_set.ym, color=c, marker='o', s=40, alpha=0.65)
        if clust_number != -1:
            cenx = np.mean(clust_set.xm)
            ceny = np.mean(clust_set.ym)
            plt.text(cenx, ceny, str(clust_number), fontsize=30, color='red', )

    plt.title(r"Weather Stations in Canada Clustered (1): $ \epsilon = 0.3$", fontsize=14)
    plt.savefig("etopo_cluster.png", dpi=300)


if __name__ == '__main__':
    main()
