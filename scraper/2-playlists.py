from base import Client
from pymongo import MongoClient
from tqdm import tqdm

import datetime as dt


BATCH_SIZE = 20

db        = MongoClient('localhost', 27017)['spotify']
users     = db['users']
playlists = db['playlists']

cl = Client('','', 30)

already_scraped = set(playlists.distinct('owner_id')) # We use a set for O(1) lookup
print(f'Number of owners/users: {len(already_scraped)}')
print(f'Unique playlists: {len(playlists.distinct("playlist_id"))}')
print(f'Number of playlists: {playlists.count_documents({})}')
data = []

count = 0
for user_id in tqdm(users.distinct('user_id'), colour='#696969', leave=True):
    # If we have already scraped playlists of this user, skip
    if user_id in already_scraped: continue
    # Note: We dont need to put an else statement, cause the users being iterated over are unique

    # Gets the playlists of this user
    new_data  = cl.get_playlists_of_user_unofficial(user_id)
    # Adds time when scraped to all dicts inside the list
    tz_info   = dt.timezone(dt.timedelta(hours=5.5))
    timestamp = dt.datetime.now(tz=tz_info)
    posix     = int(timestamp.timestamp())
    for i in new_data:
        i['time_scraped_posix'] = posix
    # Appends to `data`
    data.extend(new_data)
    
    # Save our data every BATCH_SIZE iterations
    count += 1
    if count >= BATCH_SIZE:
        if data: playlists.insert_many(data)
        data.clear()
        count = 0


# Save the data again, for the last incomplete batch
playlists.insert_many(data)

