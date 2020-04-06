import pandas as pd
from src.Processing.pre_process import ProcessData
import click
import glob

def stats(similarity_file):
    similarity_dataset = ProcessData.loadSimilarityFile(similarity_file)
    return similarity_dataset.groupby('user_id1').count().mean()['similarity']

@click.command()
@click.option('--similarity_file', help='similarity file.')
@click.option('--path', help='path folder.')
def main(similarity_file, path):
    if similarity_file:
        stats(similarity_file)

    if path:
        read_files = glob.glob("./" + str(path) + "/*.txt")
        for f in read_files:
            with open(f, "rb") as infile:
                print(str(infile.name) + " -> " + str(stats(infile)))

if __name__ == '__main__':
    main()
