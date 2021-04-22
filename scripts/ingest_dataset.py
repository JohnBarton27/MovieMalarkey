import argparse
from imdb import IMDb


parser = argparse.ArgumentParser(description='Ingests a dataset from IMDb. Expects the title.basics.tsv dataset '
                                             '(uncompressed)')
parser.add_argument('filepath', help='Filepath of title.basics.tsv dataset from IMDb')

args = parser.parse_args()

with open(args.filepath, 'r') as input_dataset:
    content = input_dataset.read()
    all_titles = content.split('\n')[1:]

    # Store all Movies we want to include in our dataset
    valid_titles = []

    for title in all_titles:
        title_pieces = title.split('\t')

        title_id = title_pieces[0]
        title_type = title_pieces[1]

        # We only care about movies - not shorts, TV series, etc.
        if title_type != 'movie':
            continue

        valid_titles.append(title)
