import pandas as pd
from src.Processing.pre_process import ProcessData
import click
import glob

def stats(similarity_file):
    similarity_dataset = ProcessData.loadSimilarityFile(similarity_file)
    return similarity_dataset.groupby('user_id1').count().mean()['similarity']

def different_items_and_pois(dataset):
    print(dataset)
    dataset_completo = ProcessData.loadData(dataset)
    different_items = list(dict.fromkeys(dataset_completo['item_id'].tolist()))
    different_users = list(dict.fromkeys(dataset_completo['user_id'].tolist()))

    return len(different_items), len(different_users)

#def stats(dataset_file):
   # dataset = ProcessData.loadData(dataset_file)
    #return dataset.groupby('user_id').count().mean()['item_id']

@click.command()
@click.option('--similarity_file', help='similarity file.')
@click.option('--path', help='path folder.')
@click.option('--statics_dataset', help='show statics dataset.')
def main(similarity_file, path, statics_dataset):
    if similarity_file:
        stats(similarity_file)

    if statics_dataset == '1':
        print(different_items_and_pois(path))

    if path:
        read_files = glob.glob("./" + str(path) + "/*.txt")
        for f in read_files:
            with open(f, "rb") as infile:
                if "stats" not in infile.name:
                    print(str(infile.name) + " -> " + str(stats(infile)))

if __name__ == '__main__':
    main()
