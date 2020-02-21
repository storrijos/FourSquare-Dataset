import pandas as pd
import click
import os
import json
import os.path
from os import path


class LineDataset:

    def __init__(self, user_id, timestamp, lat, longitude, item_id):
        self.user_id = user_id
        self.timestamp = timestamp
        self.lat = lat
        self.long = longitude
        self.item_id = item_id

    def __str__(self):
        return self.user_id + '    ' \
               + self.item_id + '    ' \
               + self.lat + '    ' \
               + self.long + '    ' \
               + self.timestamp

"""
def find_path():
    curent_file_abs_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(curent_file_abs_path)
    print(curent_file_abs_path)
    return curent_file_abs_path
"""
class ProcessData:
    def __init__(self):
        pass

    def dataset_to_list_of_lists(traj):
        string_list = list(traj.values)
        result = []
        for row in string_list:
            row = row.replace("]", "")
            row = row.replace("[", "")
            result.append([int(x) for x in row.split(',')])
        return result

    def recommender_preprocessDataset(filename):
        #find_path()
        dataset = pd.read_csv(filename, delim_whitespace=True, header=None)
        dataset.columns = ["id", "item_id", "rating", "real_timestamp"]
        dataset.sort_values(['id', 'real_timestamp'], ascending=[True, True], inplace=True)
        dataset['timestamp'] = dataset.groupby(['id']).cumcount()
        dataset = dataset.drop(columns=['real_timestamp'])
        dataset[['id', 'item_id', 'timestamp']] = dataset[['id', 'item_id', 'timestamp']].astype('int32')

        data = dataset.groupby(['id', 'item_id'], as_index=False).agg({'rating': 'sum'})

        #print(data)

        return data

    def st_dbscan_deep_search(elem, list):
        neighbors = []
        for row in list:
            if elem in row:
                neighbors.append(row)

        flatten = sum(neighbors, [])
        return [(ii, 1.0) for n, ii in enumerate(flatten) if ii not in flatten[:n] and ii != elem]

    def st_dbscan_clasify_neighbors(list):
        flatten_list = sum(list, [])
        dict = {}

        for elem in flatten_list:
            search = ProcessData.st_dbscan_deep_search(elem, list)
            if search != None:
                dict[elem] = search
        print(dict)
        return dict

    def dump_to_file(self, neighbors_classified, output):
        if path.exists(output):
            print('El fichero ' + str(output) + ' ya existe')
        else:
            print(output)
            with open(output, "a") as text_file:
                for key, elems in neighbors_classified.items():
                    for neighbor in elems:
                        text_file.write(str(key) + " " + str(neighbor[0]) + " " + str(neighbor[1]) + '\n')
    def dump_to_pandas(self, neighbors_classified):
        index = 0
        final_df = pd.DataFrame()
        for key, elems in neighbors_classified.items():
            for neighbor in elems:
                tmp_df = pd.DataFrame({
                    'user_id': key,
                    'neighbour_id': neighbor[0],
                    'weight': neighbor[1]
                }, index=[index])
                index += 1
                final_df = final_df.append(tmp_df)
        final_df.reset_index(drop=True)
        return final_df

    def flock_partial_preprocessDataset(self, filename):
        #find_path()
        #print("Reading with pandas " + filename + " --> " + os.path.realpath(filename))
        dataset = pd.read_csv(filename, delim_whitespace=True, header=None)
        dataset.columns = ["id", "item_id", "latitude", "longitude", "real_timestamp"]
        dataset.sort_values(['id', 'real_timestamp'], ascending=[True, True], inplace=True)
        #dataset['timestamp'] = dataset.groupby(['id']).cumcount()
        dataset[['id', 'item_id', 'real_timestamp']] = dataset[['id', 'item_id', 'real_timestamp']].astype('int32')
        dataset[['latitude', 'longitude']] = dataset[['latitude', 'longitude']].astype('float32')
        dataset.to_pickle('Flock_partialID.df')
        return dataset

    def flock_preprocessDataset(self, filename):
        #find_path()
        #print("Reading with pandas " + filename + " --> " + os.path.realpath(filename))
        dataset = pd.read_csv(filename, delim_whitespace=True, header=None)
        dataset.columns = ["id", "item_id", "latitude", "longitude", "real_timestamp"]
        dataset.sort_values(['id', 'real_timestamp'], ascending=[True, True], inplace=True)
        dataset['timestamp'] = dataset.groupby(['id']).cumcount()
        dataset[['id', 'item_id','timestamp', 'real_timestamp']] = dataset[['id', 'item_id','timestamp', 'real_timestamp']].astype('int32')
        dataset[['latitude', 'longitude']] = dataset[['latitude', 'longitude']].astype('float32')
        dataset = dataset.drop(columns=['item_id'])
        dataset.to_pickle('FlockID.df')
        return dataset

    def loadSimilarityFile(filename):
        data = pd.read_csv(filename, delim_whitespace=True, header=None)
        data.columns = ["user_id1", "user_id2", "similarity"]
        return data

    def loadData(filename):
        data = pd.read_csv(filename, delim_whitespace=True, header=None)
        data.columns = ["user_id", "item_id", "lat", "long", "timestamp"]
        data[['user_id', 'item_id','timestamp']] = data[['user_id', 'item_id','timestamp']].astype('int32')
        data[['lat', 'long']] = data[['lat', 'long']].astype('float32')

        summary_stats = data.describe()
        return data

    def printToFile(file, salida):
        with open(file, 'w') as f:
            for item in salida:
                f.write("%s\n" % item)

    def readPOISandCoordinates(txt_file):
        token = open(txt_file, "r")
        linestoken = token.readlines()
        poi_map = {}
        for line in linestoken:
            poi_id = line.split()[0]
            lat = line.split()[1]
            longitude = line.split()[2]
            poi_map[poi_id] = [lat, longitude]
        return poi_map

    def readFileGroupItem(txt_file, pois):
        token = open(txt_file, "r")
        linestoken = token.readlines()
        items_lines = []
        count = 1
        for line in linestoken:
            percentage = (float(count) / float(len(linestoken))) * 100
            print('Setting up items' + "%.2f" % percentage + '%')
            count += 1
            item_id = str(line.split()[1])
            user_id = line.split()[0]
            timestamp = line.split()[3]
            if item_id in pois:
                poi_lat_long = pois[item_id]
                poi_lat = poi_lat_long[0]
                poi_long = poi_lat_long[1]
            else:
                poi_lat = str(float('nan'))
                poi_long = str(float('nan'))

            line_dataset = LineDataset(user_id, timestamp, poi_lat, poi_long, item_id)
            items_lines.append(line_dataset)
        return items_lines

    def loadAndCleanDataset(input_data, output_file):
        rows_array = {}
        dataset = ProcessData.loadData(input_data)

        print(dataset)
        previous_timestamp = dataset['timestamp'].iloc[0]

#traj_dict = {3: {1: [[lat.....], [long....]], 2: [[lat.....], [long....]]}, ...}

        for index, item in dataset.iterrows():
            user_id = int(item['user_id'])
            user_dict = {}
            #Mas de 8h, otra trayectoria

            #traj_dict = {3: [[lat.....], [long....]], 15: [[lat.....], [long....]], 31: [[lat.....], [long....]]...}
            #traj_dict = {3: {1: [[lat.....], [long....]], 2: [[lat.....], [long....]]}, ...}

            if user_id in rows_array:
                if item['timestamp'] - previous_timestamp >= 28800:
                    lenght = len(rows_array[user_id])
                    rows_array[user_id][lenght] = [[None for x in range(1)] for y in range(2)]
                    rows_array[user_id][lenght][0] = [item['lat']]
                    rows_array[user_id][lenght][1] = [item['long']]
                    previous_timestamp = item['timestamp']

                else:
                    rows_array[user_id][len(rows_array[user_id])-1][0].append(item['lat'])
                    rows_array[user_id][len(rows_array[user_id])-1][1].append(item['long'])
                    previous_timestamp = item['timestamp']
            else:
                latitude = [item['lat']]
                rows_array[user_id] = {}
                rows_array[user_id][0] = [[None for x in range(1)] for y in range(2)]
                rows_array[user_id][0][0] = latitude
                longitude = [item['long']]
                rows_array[user_id][0][1] = longitude
                previous_timestamp = item['timestamp']

        print(rows_array)
        for key, value in rows_array.items():
            rows_array[key] = [rows_array[key]]

        with open(output_file, 'a') as file:
            file.write(json.dumps(rows_array))

        return rows_array

@click.command()
@click.option('--method', default='save_dataset', help='Method.')
@click.option('--input_file', default='US_NewYorkTempTrain.txt', help='Dataset.')
@click.option('--coords_file', default='POIS_Coords_Foursquaretxt', help='Dataset.')
@click.option('--output_file', default='US_NewYorkTempTrain_short.txt', help='Dataset.')
def main(method, input_file, coords_file, output_file):
    if method == 'dataset_similarity':
        ProcessData.loadAndCleanDataset(input_file, output_file)
    else:
        save_dataset_with_coords(input_file, coords_file, output_file)

def save_dataset_with_coords(input_file, coords_file, output_file):
    pois_coords = ProcessData.readPOISandCoordinates(coords_file)
    salida = ProcessData.readFileGroupItem(input_file, pois_coords)
    ProcessData.printToFile(str(output_file), salida)

if __name__ == '__main__':
    main()
    #ProcessData.loadAndCleanDataset('US_NewYork_POIS_Coords_shortCompleto.txt', 'file2.txt')
    #ProcessData.loadAndCleanDataset('US_NewYork_POIS_Coords_shortCompleto2.txt')

    #save_dataset_with_coords()


