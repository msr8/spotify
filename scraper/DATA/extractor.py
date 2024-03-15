import pandas as pd
import os
from tqdm import tqdm

# Setting low_memory=False
# https://stackoverflow.com/questions/24251219/pandas-read-csv-low-memory-and-dtype-options

TQDM_CONFIG = {
    'colour': '#696969',
    'leave':  True,
}

ORIGINAL_FP = 'track_ids_datasets.txt'
DATASETS    = '../../SPOTIFY_DATASETS'

if not os.path.exists(ORIGINAL_FP):
    with open(ORIGINAL_FP, 'w') as f:
        f.write('')

with open(ORIGINAL_FP) as f:
    track_ids = set(f.read().splitlines()) # We use a set for O(1) lookup
    if '' in track_ids: track_ids.remove('')






def asaniczka() -> None:
    '''
    4177 tracks
    '''
    fp = os.path.join(DATASETS, 'asaniczka-universal_top_spotify_songs.csv')
    # Extract the track IDs
    data = pd.read_csv(fp)['spotify_id']
    # Update the original set
    track_ids.update(data)
    # Save the data
    with open(ORIGINAL_FP, 'w') as f:
        f.write('\n'.join(track_ids))


def conorvaneden() -> None:
    # Cant do anything cause track IDs are not present in the dataset UGH
    pass


def edumucelli() -> None:
    '''
    21746 tracks
    21626 tracks not in previous datasets (120 already present)
    21626 + 4177 = 25803
    - Some values in the "URL" column are nan for some reason
    - Altho 3,441,198 enteries are present in the CSV file, there are a TON of duplicates
    - Also 9 NaN values in the URL section
    '''
    fp = os.path.join(DATASETS, 'edumucelli.csv')
    # Extract the track IDs
    data = pd.read_csv(fp)['URL']
    data.dropna(inplace=True)
    data.drop_duplicates(inplace=True)
    data = data.apply(lambda x: x.split('/')[-1])
    # Update the original set
    track_ids.update(data)
    # Save the data
    with open(ORIGINAL_FP, 'w') as f:
        f.write('\n'.join(track_ids))


def fcpercival() -> None:
    '''
    169907 tracks
    167786 tracks not in previous datasets (2121 already present)
    167786 + 25803 = 193589
    '''
    fp = os.path.join(DATASETS, 'fcpercival/data.csv')
    # Extract the track IDs
    data = pd.read_csv(fp)['id']
    # Update the original set
    track_ids.update(data)
    # Save the data
    with open(ORIGINAL_FP, 'w') as f:
        f.write('\n'.join(track_ids))


def joebeachcapital() -> None:
    '''
    32833 tracks
    21075 tracks not in previous datasets (11758 already present)
    21075 + 193589 = 214664
    '''
    fp = os.path.join(DATASETS, 'joebeachcapital/spotify_songs.csv')
    # Extract the track IDs
    data = pd.read_csv(fp)['track_id']
    # Update the original set
    track_ids.update(data)
    # Save the data
    with open(ORIGINAL_FP, 'w') as f:
        f.write('\n'.join(track_ids))


def leonardopena() -> None:
    # Cant do anything cause track IDs are not present in the dataset UGH
    pass


def mrmorj() -> None:
    '''
    42305 tracks
    30284 tracks not in previous datasets (12021 already present)
    30284 + 214664 = 244948
    '''
    fp = os.path.join(DATASETS, 'mrmorj/genres_v2.csv')
    # Extract the track IDs
    data = pd.read_csv(fp, low_memory=False)['id'] # https://stackoverflow.com/a/69969188/17002774
    # Update the original set
    track_ids.update(data)
    # Save the data
    with open(ORIGINAL_FP, 'w') as f:
        f.write('\n'.join(track_ids))


def nelgiriyewithana() -> None:
    # Cant do anything cause track IDs are not present in the dataset UGH
    pass


def rodolfofigueroa() -> None:
    '''
    1204025 tracks
    1176943 tracks not in previous datasets (27082 already present)
    1176943 + 244948 = 1421891
    '''
    fp = os.path.join(DATASETS, 'rodolfofigueroa.csv')
    # Extract the track IDs
    data = pd.read_csv(fp)['id']
    print('uhh', len(data))
    # Update the original set
    track_ids.update(data)
    # Save the data
    with open(ORIGINAL_FP, 'w') as f:
        f.write('\n'.join(track_ids))







if __name__ == '__main__':
    funcs = [asaniczka, edumucelli, fcpercival, joebeachcapital, mrmorj, rodolfofigueroa]

    pbar = tqdm(total=len(funcs), **TQDM_CONFIG)
    for func in funcs:
        pbar.set_description(func.__name__)
        func()
        pbar.update(1)
        print(len(track_ids))
