
from os import path
import os
import src.Processing.pre_process as ProcessData
import click
import pandas as pd
import src.Patterns.Flock.fpFlockOnline as FPFlockOnline
import src.Patterns.Convoy.ConvoyTrajectory as ConvoyTrajectory
import glob


class ConvoyPartial(object):

    def convoy_partial(self, dataset, similarity_file, k, output, minpoints, lifetime, distance_max, partials):
        pois_coords_dataset = ProcessData.ProcessData.flock_preprocessDataset(self, dataset)

        similarity = pd.read_csv(similarity_file, delim_whitespace=True, header=None)
        similarity.columns = ["user_id1", "user_id2", "similarity"]

        #similarity[['user_id1', 'similarity']].sort_values('similarity', ascending=False).groupby('user_id1').head(k)

        #similarity_sorted = similarity.groupby(["user_id1"]).apply(lambda x: x.sort_values(["similarity"], ascending=False)).head(2)

        similarity_sorted = similarity.sort_values('similarity', ascending=False).groupby('user_id1').head(k)

        groups = similarity_sorted.groupby('user_id1')['user_id2'].apply(list).to_dict()
        #print('SORTED')
        #print(similarity_sorted)

        pre_flock_csv_names = {}

        for user_id1, users in groups.items():
            users.append(user_id1)
            partial_dataframe = pois_coords_dataset[pois_coords_dataset['id'].isin(users)]
            #print(partial_dataframe)
            if not partial_dataframe.empty:
                partial_dataframe.to_csv('src/Patterns/Convoy/' + str(user_id1) + 'partial_in.txt', index=False, header=None, sep=' ')
                partial_dataframe.reset_index()
                pre_flock_csv_names[str(user_id1) + 'partial_in.txt'] = str(user_id1) + 'partial_out.txt'

        for csv_in, csv_out in pre_flock_csv_names.items():
            ConvoyTrajectory.convoy_partials('src/Patterns/Convoy/' + csv_in, csv_out, minpoints, lifetime, distance_max, partials)
            if path.exists('src/Patterns/Convoy/' + csv_in):
                os.remove('src/Patterns/Convoy/' + csv_in)
            if path.exists(('src/Patterns/Convoy/' + csv_in).rsplit('.', 1)[0] + '_temp_output' + '.csv'):
                os.remove(('src/Patterns/Convoy/' + csv_in).rsplit('.', 1)[0] + '_temp_output' + '.csv')

        with open(output, "wb") as outfile:
            read_files = glob.glob("./src/Patterns/Convoy/*out.txt")
            print(read_files)
            for f in read_files:
                with open(f, "rb") as infile:
                    print(infile)
                    outfile.write(infile.read())

@click.command()
@click.option('--dataset', default='US_NewYork_POIS_Coords_short.txt', help='Dataset.')
@click.option('--similarity_file', default='similarity_output_convoy.txt', help='Output file.')
@click.option('--k', default=10, help='K neighbors.')
@click.option('--output', default='similarity_output_convoy.txt', help='Output file.')
@click.option('--minpoints', default=2, help='Minimum number of points.')
@click.option('--lifetime', default=2, help='Minimum trajectory Lifetime.')
@click.option('--distance_max', default=0.2, help='Maximum distance between points.')
@click.option('--partials', default=False, help='Partials trajectories')

def calculate_convoy_partial(dataset, similarity_file, k, output, minpoints, lifetime, distance_max, partials):
    if path.exists(output):
        print('El fichero ' + str(output) + ' ya existe')
        return

    convoy_function = ConvoyPartial()
    convoy_function.convoy_partial(dataset, similarity_file, k, output, minpoints, lifetime, distance_max, partials)


if __name__ == '__main__':
    calculate_convoy_partial()
