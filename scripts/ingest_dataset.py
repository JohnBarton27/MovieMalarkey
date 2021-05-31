import argparse
from imdb import IMDb
import os
import pathlib


parser = argparse.ArgumentParser(description='Ingests a dataset from IMDb. Expects the title.basics.tsv dataset '
                                             '(uncompressed)')
parser.add_argument('filepath', help='Filepath of title.basics.tsv dataset from IMDb')

args = parser.parse_args()

# Get location of Movie Malarkey source (for proper placement of stripped dataset)
movie_malarkey_loc = pathlib.Path(__file__).parent.parent.absolute()

with open(args.filepath, 'r') as input_dataset:
    content = input_dataset.read()
    header = content.split('\n')[0]
    all_titles = content.split('\n')[1:]

    # Connect to IMDb vi IMDbPY
    ia = IMDb()

    # Store all Movies we want to include in our dataset
    valid_titles = []

    idx = 0
    for title in all_titles:
        idx += 1
        print(f'Checking title {idx} of {len(all_titles)} ({len(valid_titles)} valid)...')
        title_pieces = title.split('\t')

        title_id = title_pieces[0].split("tt")[-1]
        title_type = title_pieces[1]

        # We only care about movies - not shorts, TV series, etc.
        if title_type != 'movie':
            continue

        imdbpy_movie = ia.get_movie(title_id)

        try:
            plot = imdbpy_movie['plot']
        except KeyError:
            # Contained no plot - is no good to us!
            continue

        valid_titles.append(title)

        # TODO remove temp early exit
        if len(valid_titles) >= 100:
            break

    print(f'Started with {len(all_titles)} titles, ended with {len(valid_titles)} usable movies.')

    # Write valid titles to new file
    dataset_dir = pathlib.Path.joinpath(movie_malarkey_loc, 'dataset')
    if not os.path.exists(dataset_dir):
        os.mkdir(dataset_dir)
        
    with open(pathlib.Path.joinpath(dataset_dir, 'malarkey.tsv'), 'w') as dest_file:
        dest_file.write(header + '\n')

        for valid_title in valid_titles:
            dest_file.write(valid_title + '\n')
