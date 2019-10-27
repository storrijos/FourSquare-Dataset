from datetime import datetime
import pandas as pd
import numpy as np
from src.Patterns.ST_DBSCAN.stdbscan import STDBSCAN
import pyproj
import matplotlib.pyplot as plt
from src.Processing.pre_process import ProcessData
import os

class STDBscan():

    def __init__(self):
        self.result = []

    def undo_projection(self, df, p1_str='epsg:3857', p2_str='epsg:4326'):
        inProj = pyproj.Proj(init=p1_str)
        outProj = pyproj.Proj(init=p2_str)
        lon = df['long'].values
        lat = df['lat'].values
        x1,y1 = lon,lat
        x2,y2 = pyproj.transform(inProj,outProj,x1,y1)

        df['long'] = x2
        df['lat'] = y2

        return df

    def plot_clusters(self, df, output_name):

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

    def stdbscan_neighbors(self, df, result):
        i = pd.merge(df, result, left_index=True, right_index=True)
        elems = i.groupby('cluster').user_id.apply(list)
        #Remove the ones without cluster
        del elems[-1.0]
        print('elems')
        print(elems.values)
        neighbors = ProcessData.st_dbscan_clasify_neighbors(elems.values)
        print('vecinos')
        print(neighbors)
        print('##')
        return neighbors

    def dump_to_file(self, neighbors_classified):
        if neighbors_classified is not None:
            process = ProcessData()
            final_df = process.dump_to_pandas(neighbors_classified)
            curent_file_abs_path = os.path.dirname(os.path.realpath(__file__))
            final_df.to_csv(str(curent_file_abs_path) + "/../../Recommender/st_dbscan_neighbors_classified.txt", sep=" ", encoding='utf-8', index=False, header=False)

    def execute_stdbscan(self, filename, spatial_thresold=5000, temporal_threshold=6000, min_neighbors=1):
        curent_file_abs_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(curent_file_abs_path)

        df = ProcessData.loadData(filename)
        '''
        transfrom the lon and lat to x and y
        need to select the right epsg
        I don't the true epsg of sample, but get the same result by using 
        epsg:4326 and epsg:32635
        '''

        st_dbscan = STDBSCAN(col_lat='lat', col_lon='long',
                             col_time='timestamp', spatial_threshold=spatial_thresold,
                             temporal_threshold=temporal_threshold, min_neighbors=min_neighbors)

        df = st_dbscan.projection(df)
        print('########################## PROJECTION #########################')
        print(df)

        result = st_dbscan.run(df)
        neighbors = self.stdbscan_neighbors(df, result)
        print(neighbors)
        self.result = result
        self.dump_to_file(neighbors)
        return neighbors

    def stdbscan_plot_clusters(self):
        pd.DataFrame(self.execute_stdbscan())
        df = self.undo_projection(self.result)
        self.plot_clusters(df, 'output')

if __name__ == '__main__':
    st = STDBscan()
    st.stdbscan_plot_clusters()

    #df = pd.DataFrame(test_time())
    #print(pd.value_counts(df['cluster']))
    #plot_clusters(df, 'output')
    #df = undo_projection(df)
    #plot_clusters(df, 'output')
