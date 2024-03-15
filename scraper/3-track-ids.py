from base import Client
from pymongo import MongoClient
from tqdm import tqdm
from sty import fg, ef

import datetime as dt
from sys import getsizeof as sizeof
import os

BATCH_SIZE = 1000

TRACK_IDS_DIR      = 'DATA/TRACK_IDS'
ALREADY_SCRAPED_FP = 'DATA/playlists_whose_tracks_have_been_scraped.txt'
DB                 = MongoClient('localhost', 27017)['spotify']
playlists          = DB['playlists']
cl                 = Client()


os.makedirs(TRACK_IDS_DIR, exist_ok=True)

fns = [0]
for fn_ext in os.listdir(TRACK_IDS_DIR):
    fn = fn_ext.split('.')[0]
    fns.append(int(fn))
curr_fn = max(fns) + 1


if os.path.exists(ALREADY_SCRAPED_FP):
    with open(ALREADY_SCRAPED_FP, 'r') as f:
        already_scraped = set(f.read().split('\n'))
        if '' in already_scraped: already_scraped.remove('')
else:
    already_scraped = set()



# print(sizeof(track_ids))



print(f'{fg(215,0,215)}Number of playlists: {ef.bold}{playlists.count_documents({}) :,}{fg.rs}{ef.rs}')
print(f'{fg(215,0,215)}Number of unique playlists: {ef.bold}{len(set([x["playlist_id"] for x in playlists.find({}, {"_id": 0, "playlist_id": 1})])) :,}{fg.rs}{ef.rs}') # Not using distinct() because of the 16mb cap, and I cannot reduce it because cannot give a projection arg
print(f'{fg(215,0,215)}Number of playlists already scraped: {ef.bold}{len(already_scraped)}{fg.rs}{ef.rs}')
print(f'{fg(215,0,215)}Number of files in track IDs dir: {ef.bold}{curr_fn-1}{fg.rs}{ef.rs}')
print('\n')



count = 0
data = []
# We are doing it like this as to not trigger the 16mb limit of MongoDB
# Remember, playlist_ids ALWAYS begins with a number for some reason (and altho i havent encountered a playlis_id beginning with 8,9,or 0, its not far-fetched to assume that they will in the future)
for i in '0123456789':
    records      = playlists.find({'playlist_id': {'$regex': f'^{i}'}}, {'_id': 0, 'playlist_id': 1})
    playlist_ids = [ i['playlist_id'] for i in records ]

    for playlist_id in tqdm(playlist_ids , colour='#696969', leave=True, desc=i):
        # If we have already scraped tracks of this playlist, skip
        if playlist_id in already_scraped: continue

        # Gets the track_ids of tracks in this playlist
        try:
            new_data = cl.get_tracks_in_playlist_unofficial(playlist_id)
        except Exception as e:
            print(f'Error when scraping {playlist_id}: {e}')
            exit()
        # Add the track_ids to our `data` list
        data.extend(new_data)
        # Add this playlist_id to our set
        already_scraped.add(playlist_id)

        count += 1
        # Save our data every BATCH_SIZE playlists
        if count >= BATCH_SIZE:
            with open(ALREADY_SCRAPED_FP, 'w') as f: f.write('\n'.join(already_scraped))
            with open(f'{TRACK_IDS_DIR}/{curr_fn}.txt', 'w') as f:
                f.write('\n'.join(data))
                curr_fn += 1
            print(f'Saved {ef.bold}{fg(0,255,0)}{len(data)}{fg.rs}{ef.rs} new tracks in {ef.bold}{fg(0,255,0)}{curr_fn-1}.txt{fg.rs}{ef.rs}')
            count = 0
            data.clear()


# Save the data again, for the last incomplete batch
with open(ALREADY_SCRAPED_FP, 'w') as f: f.write('\n'.join(already_scraped))
with open(f'{TRACK_IDS_DIR}/{curr_fn}.txt', 'w') as f:
    f.write('\n'.join(data))







