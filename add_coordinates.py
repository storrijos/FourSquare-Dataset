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

def main():
    pois_coords = readPOISandCoordinates('entradas/DatosNewYork/POIS_Coords_Foursquare.txt')
    salida = readFileGroupItem('entradas/DatosNewYork/US_NewYorkTempTrain.txt', pois_coords)
    printToFile('salidas/US_NewYork_POIS_Coords', salida)

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
        long = line.split()[2]
        poi_map[poi_id] = [lat, long]
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

if __name__ == '__main__':
    main()
