from datetime import datetime
import pandas as pd
import numpy as np
from stdbscan import STDBSCAN
import pyproj

import os, sys
curent_file_abs_path = os.path.abspath(__file__)
current_dir = os.path.dirname(curent_file_abs_path) + "/../../Processing"
carpeta2_abs_path = os.path.abspath(current_dir)
sys.path.insert(0,carpeta2_abs_path)
from pre_process import ProcessData


def undo_projection(df, p1_str='epsg:3857', p2_str='epsg:4326'):
    inProj = pyproj.Proj(init=p1_str)
    outProj = pyproj.Proj(init=p2_str)
    lon = df['long'].values
    lat = df['lat'].values
    x1,y1 = lon,lat
    x2,y2 = pyproj.transform(inProj,outProj,x1,y1)

    df['long'] = x2
    df['lat'] = y2

    return df

def plot_clusters(df, output_name):
    import matplotlib.pyplot as plt

    labels = df['cluster'].values
    X = df[['lat', 'long']].values

    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each)
              for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = (labels == k)

        xy = X[class_member_mask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=6)

    plt.title('ST-DSCAN: #n of clusters {}'.format(len(unique_labels)))
    plt.show()
    # plt.savefig(output_name)


def test_time():

    df = ProcessData.loadData('US_NewYork_POIS_Coords_short.txt')
    '''
    transfrom the lon and lat to x and y
    need to select the right epsg
    I don't the true epsg of sample, but get the same result by using 
    epsg:4326 and epsg:32635
    '''
    
    st_dbscan = STDBSCAN(col_lat='lat', col_lon='long',
                         col_time='timestamp', spatial_threshold=500,
                         temporal_threshold=6000, min_neighbors=1)

    df = st_dbscan.projection(df)
    print('########################## PROJECTION #########################')
    print(df)
    
    result_t600 = st_dbscan.run(df)

    return result_t600

if __name__ == '__main__':
    df = pd.DataFrame(test_time())
    print(pd.value_counts(df['cluster']))
    #plot_clusters(df, 'output')
    df = undo_projection(df)
    plot_clusters(df, 'output')

