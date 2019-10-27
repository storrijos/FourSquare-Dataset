import folium
from folium import Choropleth, Circle, Marker
from folium.plugins import HeatMap, MarkerCluster
from folium import Marker, GeoJson
from folium.plugins import HeatMap
from IPython.display import IFrame
import pandas as pd
import geopandas as gpd
import math
from shapely.geometry import Point
from shapely.ops import nearest_points

# Function for displaying the map
from sklearn.cluster import DBSCAN


def embed_map(m, file_name):
    m.save(file_name)
    print('guarda')
    return IFrame(file_name, width='100%', height='500px')

def loadData(filename):
    # Load the data
    data = pd.read_csv(filename, delim_whitespace=True, header=None)
    data.columns = ["user_id", "item_id", "lat", "long", "timestamp"]

    # Drop rows with missing locations
    data.dropna(subset=['lat', 'long'], inplace=True)
    # Print the first five rows of the table
    return data

def representaNormal(data):
    # Create a map
    m_2 = folium.Map(location=[40.755881, -73.985778], tiles='openstreetmap', zoom_start=10)

    # Add points to the map
    for idx, row in data.iterrows():
        Marker([row['lat'], row['long']]).add_to(m_2)

    # Display the map
    embed_map(m_2, 'map_normal.html')

def representaCluster(data):
    # Create the map
    m_3 = folium.Map(location=[40.755881, -73.985778], tiles='openstreetmap', zoom_start=10)

    # Add points to the map
    mc = MarkerCluster()
    for idx, row in data.iterrows():
        if not math.isnan(row['long']) and not math.isnan(row['lat']):
            mc.add_child(Marker([row['lat'], row['long']]))
    m_3.add_child(mc)

    # Display the map
    embed_map(m_3, 'map_cluster.html')

def loadGeometryDataset(filename):
    data_pandas = loadData(filename)
    data_geometry = gpd.GeoDataFrame(data_pandas,
                                  geometry=gpd.points_from_xy(data_pandas.long, data_pandas.lat))

    # Set the coordinate reference system (CRS) to EPSG 4326
    data_geometry.crs = {'init': 'epsg:4326'}

    #print(data_geometry.head())
    return data_geometry

def check_proximity(data):
    data.insert(5, 'nearest_geometry', None)
    data.insert(6, 'centroid', None)

    for index, row in data.iterrows():
        point = row.geometry
        multipoint = data.drop(index, axis=0).geometry.unary_union
        queried_geom, nearest_geom = nearest_points(point, multipoint)
        data.loc[index, 'nearest_geometry'] = nearest_geom

    data["centroid"] = data.centroid

    # Measure distance from release to each station
    #distances = data.geometry.distance(data.geometry)
    return data


def DBSCAN_with_max_size(data, eps=5, max_size=2):
    clusters = DBSCAN(eps=3, min_samples=2).fit(data['lat', 'long'])
    print(clusters.labels_)

def plot_proximity_map(data):

    # Create map with release incidents and monitoring stations
    m = folium.Map(location=[40.755881, -73.985778], tiles='openstreetmap', zoom_start=10)
    HeatMap(data=data[['lat', 'long']], radius=15).add_to(m)
    for idx, row in data.iterrows():
        Marker([row['lat'], row['long']]).add_to(m)
        #Marker([row["centroid"]]).add_to(m)

    DBSCAN_with_max_size(data, eps=2, max_size=5)
    # Plot each polygon on the map
    buffer = data.geometry.buffer(0.05)
    GeoJson(buffer.to_crs(epsg=4326)).add_to(m)

    # Show the map
    embed_map(m, 'map_proximity.html')

def main():
    data = loadData('../../salidas/US_NewYork_POIS_Coords_short.txt')
    representaCluster(data)
    geometry_data = loadGeometryDataset('../../salidas/US_NewYork_POIS_Coords_short.txt')
    geometry_data = check_proximity(geometry_data)
    print(geometry_data.head().to_string())
    plot_proximity_map(geometry_data)

if __name__ == '__main__':
    main()
