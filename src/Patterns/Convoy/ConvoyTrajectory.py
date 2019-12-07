from TrajectoryParser import TrajectoryParser
from CMC import CMC
from src.Processing.pre_process import ProcessData
import pandas as pd
import click
import os

def convoy_preprocessDataset(filename):
    dataset = pd.read_csv(filename, delim_whitespace=True, header=None)
    dataset.columns = ["obj_id", "item_id", "x", "y", "t"]
    dataset.sort_values(['obj_id', 't'], ascending=[True, True], inplace=True)
    dataset['t'] = dataset.groupby(['obj_id']).cumcount() + 1
    dataset = dataset.drop(columns=['item_id'])

    header = ["obj_id", "t", "x", "y"]
    dataset.to_csv(filename.rsplit('.', 1)[0] + '_temp_output' + '.csv', columns=header, index=False, sep=',')

    return dataset

def dataset_to_list_of_lists(dataset):
    string_list = list(dataset.traj.values)
    result = []
    for row in string_list:
        # row = row.replace("]", "")
        # row = row.replace("[", "")
        result.append([int(x) for x in row.split(',')])
    return result


def deep_search(elem, list):
    neighbors = []
    for row in list:
        if elem in row:
            neighbors.append(row)

    flatten = sum(neighbors, [])
    return [(ii, 1.0) for n, ii in enumerate(flatten) if ii not in flatten[:n] and ii != elem]


def clasify_neighbors(list):
    flatten_list = sum(list, [])
    dict = {}

    for elem in flatten_list:
        search = deep_search(elem, list)
        if search != None:
            dict[elem] = search
    return dict

def dump_to_file(neighbors_classified, output):
    process = ProcessData()
    """
    final_df = process.dump_to_pandas(neighbors_classified)
    final_df.to_csv(output, sep=" ", encoding='utf-8', index=False, header=False)
    """
    process.dump_to_file(neighbors_classified, output)

def printFinalResultDataFrame(df, output):
    # Remove Duplicates from DataFrame
    df = df.drop_duplicates(subset=['begin', 'end', 'traj']).apply(list)
    neighbors_classified = clasify_neighbors(dataset_to_list_of_lists(df))
    return dump_to_file(neighbors_classified, output)

def toPandasFormat(res):
    df = pd.DataFrame(columns=['begin', 'end', 'lifetime', 'traj'])
    for conv in res:
        partial_res = ""
        flag = 1
        for oid in conv.cluster:
            if flag:
                partial_res += " " + str(oid)
                flag = 0
            else:
                partial_res += ", " + str(oid)

        data = {'begin': conv.getStartTime(), 'end': conv.getEndTime(), 'lifetime': conv.getLifetime(),
                'traj': str(partial_res)}
        df = df.append(data, ignore_index=True)

    return df

@click.command()
@click.option('--filename', default='US_NewYork_POIS_Coords_short.txt', help='Dataset.')
@click.option('--output', default='convoy_neighbors_classified.txt', help='Output file.')
@click.option('--minpoints', default=2, help='Minimum number of points.')
@click.option('--lifetime', default=2, help='Minimum trajectory Lifetime.')
@click.option('--distance_max', default=0.2, help='Maximum distance between points.')
@click.option('--partials', default=False, help='Partials trajectories')

def convoy(filename, output, minpoints, lifetime, distance_max, partials):
    dataset = convoy_preprocessDataset(filename)
    parser = TrajectoryParser(filename.rsplit('.', 1)[0] + '_temp_output' + '.csv')
    # obj_id, t, x, y
    traj_set = parser.get_traj_set()
    # minPoints, #lifetime, #distance_max
    res = CMC.cm_clustering(traj_set, minpoints, lifetime, distance_max, partials)
    print("\n")
    printFinalResultDataFrame(toPandasFormat(res), output)
    for conv in res:
        with open(output.rsplit('.', 1)[0] + '_trajectory_output' + '.txt', "a") as text_file:
            text_file.write(conv.toString())
        print(conv.toString())

if __name__ == '__main__':
    convoy()
