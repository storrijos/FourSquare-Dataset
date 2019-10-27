import pandas as pd

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
        dataset = pd.read_csv(filename, delim_whitespace=True, header=None)
        dataset.columns = ["id", "item_id", "latitude", "longitude", "real_timestamp"]
        dataset.sort_values(['id', 'real_timestamp'], ascending=[True, True], inplace=True)
        dataset['timestamp'] = dataset.groupby(['id']).cumcount()
        dataset = dataset.drop(columns=['latitude', 'longitude', 'real_timestamp'])
        dataset['rating'] = 1  # np.random.randint(1, 5, len(dataset))
        return dataset

    def deep_search(elem, list):

        neighbors = []
        for row in list:
            if elem in row:
                neighbors.append(row)

        flatten = sum(neighbors, [])
        return [ii for n, ii in enumerate(flatten) if ii not in flatten[:n] and ii != elem]

    def clasify_neighbors(list):

        flatten_list = sum(list, [])
        dict = {}

        for elem in flatten_list:
            search = deep_search(elem, list)
            if search != None:
                dict[elem] = search
        print(dict)

    def flock_preprocessDataset(self, filename):
        dataset = pd.read_csv(filename, delim_whitespace=True, header=None)
        dataset.columns = ["id", "item_id", "latitude", "longitude", "real_timestamp"]
        dataset.sort_values(['id', 'real_timestamp'], ascending=[True, True], inplace=True)
        dataset['timestamp'] = dataset.groupby(['id']).cumcount()
        dataset = dataset.drop(columns=['item_id'])
        return dataset

    def printToFile(self, file, salida):
        with open(file, 'w') as f:
            for item in salida:
                f.write("%s\n" % item)

    def readPOISandCoordinates(self, txt_file):
        token = open(txt_file, "r")
        linestoken = token.readlines()
        poi_map = {}
        for line in linestoken:
            poi_id = line.split()[0]
            lat = line.split()[1]
            longitude = line.split()[2]
            poi_map[poi_id] = [lat, longitude]
        return poi_map

    def readFileGroupItem(self, txt_file, pois):
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

    def save_dataset_with_coords(self):
        pois_coords = self.readPOISandCoordinates('entradas/DatosNewYork/POIS_Coords_Foursquare.txt')
        salida = self.readFileGroupItem('entradas/DatosNewYork/US_NewYorkTempTrain.txt', pois_coords)
        self.printToFile('salidas/US_NewYork_POIS_Coords', salida)

    def loadData(filename):
        data = pd.read_csv(filename, delim_whitespace=True, header=None)
        data.columns = ["user_id", "item_id", "lat", "long", "timestamp"]
        summary_stats = data.describe()
        print(summary_stats.to_string())
        return data


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
