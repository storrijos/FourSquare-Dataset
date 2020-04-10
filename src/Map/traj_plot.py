import random
import gmplot
import click
import pandas as pd
from functools import reduce
import json

class TrajPlot(object):

    def get_random_hex(self):
        random_number = random.randint(0, 16777215)
        # convert to hexadecimal
        hex_number = str(hex(random_number))
        # remove 0x and prepend '#'
        return '#' + hex_number[2:]

    def average(self, lst):
        return sum(lst) / len(lst)

    def plot_traj(self, trajs, plotname):

        gmap = gmplot.GoogleMapPlotter(self.average(trajs[0][0]), self.average(trajs[0][1]), 11)
        for traj in trajs:
            # now let's plot:
            gmap.plot(traj[0], traj[1], self.get_random_hex(), edge_width=5)
            gmap.scatter(traj[0], traj[1], '#3B0B39', size=70, marker=False)

        #marker_locations = []
        #for traj in trajs:
        #    marker_locations.append((traj[0], traj[1]))

        gmap.apikey = "AIzaSyCbVHx4f2FGjJkZCz5yMNtvlwqpiiJ-F_U"
        gmap.draw(plotname)

        return gmap


    def plot_traj_web(self, trajs, plotname, users_colors):

        gmap = gmplot.GoogleMapPlotter(self.average(trajs[0][1][0]), self.average(trajs[0][1][1]), 11)
        #print(trajs)
        print('estamos')
        for tuple in trajs:
            user_id = tuple[0]
            traj = tuple[1]
            print('entra')
            #print(users_colors)
            # now let's plot:
            if str(user_id) in users_colors:
                color = users_colors[str(user_id)]
            else:
                print('MAL FATAL')
                color = self.get_random_hex()
            gmap.plot(traj[0], traj[1], color, edge_width=5)
            gmap.scatter(traj[0], traj[1], '#3B0B39', size=70, marker=False)

        #marker_locations = []
        #for traj in trajs:
        #    marker_locations.append((traj[0], traj[1]))

        gmap.apikey = "AIzaSyCbVHx4f2FGjJkZCz5yMNtvlwqpiiJ-F_U"
        gmap.draw(plotname)

        return gmap

    def flatten_dict_dicts(self, dict):
        coords = []
        lat = []
        long = []
        for key, values in dict[0].items():
            for lats in values[0]:
                lat.append(lats)
            for longs in values[1]:
                long.append(longs)
        coords.append(lat)
        coords.append(long)
        return coords

def read_similarity_dataset(similarity_dataset):
    data = pd.read_csv(similarity_dataset, delim_whitespace=True, header=None)
    data.columns = ["user1_id", "user2_id", "similarity"]
    data[['user1_id', 'user2_id']] = data[['user1_id', 'user2_id']].astype('int32')
    data[['similarity']] = data[['similarity']].astype('float32')
    return data

def read_similarity_file(similarity_dataset, k):
    data = read_similarity_dataset(similarity_dataset)
    return data.sort_values(by='similarity',ascending=False).head(k)

def ascending_order(dataset, k):
    if k != 0:
        return dataset.sort_values(by='similarity', ascending=False).head(k)
    else:
        return dataset.sort_values(by='similarity', ascending=False)

def plot_k_trajs_web(user_id, dataset, similarity_dataset, output_file, k, users_colors):
    traj_plot = TrajPlot()
    with open(dataset, 'r') as inf:
        traj_data_dict = eval(inf.read())
    #traj_data_dict = json.loads(dataset)

    trajs = []
    users_dataset = read_similarity_dataset(similarity_dataset)
    users = ascending_order(users_dataset[users_dataset['user1_id'] == user_id].reset_index(), k)
    print('LONGITUD')
    print(len(users))
    for user in users.iterrows():
        trajs.append((int(user[1]['user1_id']), traj_plot.flatten_dict_dicts(traj_data_dict[str(int(user[1]['user1_id']))])))
        trajs.append((int(user[1]['user2_id']), traj_plot.flatten_dict_dicts(traj_data_dict[str(int(user[1]['user2_id']))])))
    return traj_plot.plot_traj_web(trajs, output_file, users_colors)


@click.command()
@click.option('--dataset', default='similarity.txt', help='Dataset.')
@click.option('--similarity_dataset', default='similarity.txt', help='Dataset.')
@click.option('--output_file', default='map_plot.html', help='Output file.')
@click.option('--k', default=10, help='K neighbors.')
def plot_k_trajs(dataset, similarity_dataset, output_file, k):
    traj_plot = TrajPlot()
    with open(dataset, 'r') as inf:
        traj_data_dict = eval(inf.read())

    trajs = []
    users = read_similarity_file(similarity_dataset, k)
    for user in users.iterrows():
        trajs.append(traj_plot.flatten_dict_dicts(traj_data_dict[str(int(user[1]['user1_id']))]))
        trajs.append(traj_plot.flatten_dict_dicts(traj_data_dict[str(int(user[1]['user2_id']))]))
    return traj_plot.plot_traj(trajs, output_file)

if __name__ == '__main__':
    plot_k_trajs()


#python3 src/Map/traj_plot.py --dataset file5.txt --similarity_dataset similarity_output_completo3.txt --output_file salida.html --k 10