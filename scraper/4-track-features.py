from base import Client, RateLimited
from creds import CREDS

from pymongo import MongoClient
from tqdm import tqdm
from sty import fg, ef


BATCH_SIZE = 100


creds_ptr = 0


TRACK_IDS_FP = 'DATA/track_ids.txt'
DB           = MongoClient('localhost', 27017)['spotify']
tracks_coll  = DB['tracks']
cl           = Client(*CREDS[creds_ptr])

with open(TRACK_IDS_FP, 'r') as f:
    track_ids = f.read().split('\n')
    while '' in track_ids: track_ids.remove('')

already_scraped = set([i['track_id'] for i in tracks_coll.find({}, {'_id': 0, 'track_id': 1})])



print(f'{fg(215,0,215)}Number of tracks: {ef.bold}{len(track_ids):,}{ef.rs}{fg.rs}')
print(f'{fg(215,0,215)}Number of tracks already scraped: {ef.bold}{len(already_scraped):,}{ef.rs}{fg.rs}')
print('')


curr_track_ids = []
data  = []
count = 0
for track_id in tqdm(track_ids, colour='#696969', leave=True):
    # Check if we already have this track in our DB
    if track_id in already_scraped: continue

    # Append the track_id to curr_track_ids
    curr_track_ids.append(track_id)

    # If we have reached 100 tracks, get their features
    if len(curr_track_ids) >= 100:
        # Get the features of the tracks
        while True:
            try:
                features = cl.get_tracks_features_official(curr_track_ids)
                break
            except RateLimited:
                creds_ptr += 1
                if creds_ptr >= len(CREDS):
                    print(f'{fg.red}[{cl.get_ts()}] Rate limited while getting tracks features, so now exiting{fg.rs}')
                    exit()
                print(f'{fg.red}[{cl.get_ts()}] Rate limited while getting tracks features, using creds of Test {creds_ptr+1}{fg.rs}')
                cl = Client(*CREDS[creds_ptr])

        # Add the features to the data
        data.extend(features)
        # Reset curr_track_ids
        curr_track_ids.clear()
        # Increment the count
        count += 1
        # Since track_ids are already unique, we don't need to update already_scraped
        
        # Save our data every BATCH_SIZE requests
        if count >= BATCH_SIZE:
            # Save the data
            tracks_coll.insert_many(data)
            # print(f'Saved {fg(0,255,0)}{ef.bold}{len(data)}{ef.rs}{fg.rs} tracks')
            # Reset data
            data.clear()
            # Reset the count
            count = 0



