import pandas as pd
import click
import os

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
        dataset.columns = ["id", "item_id", "latitude", "longitude", "real_timestamp"]
        dataset.sort_values(['id', 'real_timestamp'], ascending=[True, True], inplace=True)
        dataset['timestamp'] = dataset.groupby(['id']).cumcount()
        dataset = dataset.drop(columns=['latitude', 'longitude', 'real_timestamp'])
        dataset[['id', 'item_id','timestamp']] = dataset[['id', 'item_id','timestamp']].astype('int32')

        dataset['rating'] = 1  # np.random.randint(1, 5, len(dataset))
        return dataset

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

    def flock_preprocessDataset(self, filename):
        #find_path()
        dataset = pd.read_csv(filename, delim_whitespace=True, header=None)
        dataset.columns = ["id", "item_id", "latitude", "longitude", "real_timestamp"]
        dataset.sort_values(['id', 'real_timestamp'], ascending=[True, True], inplace=True)
        dataset['timestamp'] = dataset.groupby(['id']).cumcount()
        dataset[['id', 'item_id','timestamp', 'real_timestamp']] = dataset[['id', 'item_id','timestamp', 'real_timestamp']].astype('int32')
        dataset[['latitude', 'longitude']] = dataset[['latitude', 'longitude']].astype('float32')
        dataset = dataset.drop(columns=['item_id'])
        return dataset

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
            poi_lat_long = pois[item_id]
            poi_lat = poi_lat_long[0]
            poi_long = poi_lat_long[1]
            line_dataset = LineDataset(user_id, timestamp, poi_lat, poi_long, item_id)
            items_lines.append(line_dataset)
        return items_lines

@click.command()
@click.option('--input_file', default='US_NewYorkTempTrain.txt', help='Dataset.')
@click.option('--coords_file', default='POIS_Coords_Foursquaretxt', help='Dataset.')
@click.option('--output_file', default='US_NewYorkTempTrain_short.txt', help='Dataset.')
def save_dataset_with_coords(input_file, coords_file, output_file):
    pois_coords = ProcessData.readPOISandCoordinates(coords_file)
    salida = ProcessData.readFileGroupItem(input_file, pois_coords)
    ProcessData.printToFile(str(output_file), salida)

if __name__ == '__main__':
    save_dataset_with_coords()

