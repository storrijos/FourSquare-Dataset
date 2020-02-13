
from os import path
import src.Processing.pre_process as ProcessData
import click
import pandas as pd
import src.Patterns.Flock.fpFlockOnline as FPFlockOnline

class FlockPartial(object):

    def flock_partial(self, dataset, similarity_file, k, output, epsilon, mu, delta):
        pois_coords_dataset = ProcessData.ProcessData.flock_preprocessDataset(self, dataset)

        similarity = pd.read_csv(similarity_file, delim_whitespace=True, header=None)
        similarity.columns = ["user_id1", "user_id2", "similarity"]

        similarity[['user_id1', 'similarity']].sort_values('similarity', ascending=False).nlargest(k, 'similarity')

        print(similarity)

        groups = similarity.groupby('user_id1')['user_id2'].apply(list).to_dict()
        pre_flock_csv_names = {}

        for user_id1, users in groups.items():
            users.append(user_id1)
            partial_dataframe = pois_coords_dataset[pois_coords_dataset['id'].isin(users)]
            print(partial_dataframe)
            if not partial_dataframe.empty:
                partial_dataframe.to_csv('src/Patterns/Flock/' + str(user_id1) + 'partial_in.txt', index=False, header=None, sep=' ')
                partial_dataframe.reset_index()
                pre_flock_csv_names[str(user_id1) + 'partial_in.txt'] = str(user_id1) + 'partial_out.txt'

        for csv_in, csv_out in pre_flock_csv_names.items():
            FPFlockOnline.calculate_flock(csv_in, csv_out, epsilon, mu, delta)


@click.command()
@click.option('--dataset', default='US_NewYork_POIS_Coords_short.txt', help='Dataset.')
@click.option('--similarity_file', default='similarity_output_convoy.txt', help='Output file.')
@click.option('--k', default=10, help='K neighbors.')
@click.option('--output', default='similarity_output_convoy.txt', help='Output file.')
@click.option('--epsilon', default=0.2, help='Epsilon.')
@click.option('--mu', default=2, help='Mu.')
@click.option('--delta', default=0.2, help='Delta.')



def calculate_flock_partial(dataset, similarity_file, k, output, epsilon, mu, delta):
    if path.exists(output):
        print('El fichero ' + str(output) + ' ya existe')
        return

    #similarity = pd.read_csv(similarity_file, delim_whitespace=True, header=None)
    #similarity.columns = ["user_id1", "user_id2", "similarity"]

    #groups = similarity.groupby('user_id1')['user_id2'].apply(list).to_dict()

    flock_function = FlockPartial()

    flock_function.flock_partial(dataset, similarity_file, k, output, epsilon, mu, delta)

    #data = ProcessData.ProcessData.loadData(dataset)


if __name__ == '__main__':
    calculate_flock_partial()