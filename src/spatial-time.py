# Imports
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
import shapely
import matplotlib.pyplot as plt
from shapely import wkt


def loadData(filename):
    data = pd.read_csv(filename, delim_whitespace=True, header=None)
    data.columns = ["user_id", "item_id", "lat", "long", "timestamp"]
    summary_stats = data.describe()
    return data

def processData():
    # Reading the AIS data into dataframe
    df = loadData('salidas/US_NewYork_POIS_Coords_short.txt')
    # Converting the dataframe into geo datarame
    gdf = gpd.GeoDataFrame(df.drop(['lat', 'long'], axis=1), crs={'init': 'epsg:4326'}, geometry=[shapely.geometry.Point(xy) for xy in zip(df.lat, df.long)])
    gdf.head()
    ax = gdf.plot(figsize=(25, 25), markersize=5)
    plt.show()
    print('a')

    # Retriving the shape file and storng it into a geo dataframe
    ports = gpd.read_file('assignment3shapefile.shp')
    allPorts = ports.set_index(['port_name'])
    allPorts.head()

    # Finding centroids of all polygons
    allPorts['centroids'] = allPorts['geometry'].centroid
    allPorts.head()

    # Creating buffers around each polygons
    allPorts['buffer'] = allPorts.geometry.buffer(2)
    buffers = allPorts['buffer']
    buffers_final = gpd.GeoDataFrame(buffers, columns=['geometry'])

    # Finding the AIS messages that intersect with each buffer of all the ports
    joins = gpd.sjoin(gdf, allPorts, how="inner", op="within")
    joins.head()

    # Creating df for message density for each port(will be used in question 6)
    countsOfPorts = joins['index_right'].value_counts()
    eachPortDensity = countsOfPorts.to_frame().reset_index()
    eachPortDensity

    # Plotting all the AIS Messages which intersect with ports
    fig, ax = plt.subplots(figsize=(200, 200))
    allPorts.plot(ax=ax, facecolor='pink')
    joins.plot(ax=ax, color='black', markersize=100)
    plt.tight_layout()
    plt.show()

def main():
    processData()

if __name__ == '__main__':
    main()
