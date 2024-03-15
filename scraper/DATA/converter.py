from pandas import read_csv
from pymongo import MongoClient
from tqdm import tqdm

client    = MongoClient('localhost', 27017)
print('Connection established')
db        = client['spotify']
# db.drop_collection('playlists')
playlists = db['users']

df = read_csv('DATA/users.csv')

for i, row in tqdm(df.iterrows(), total=len(df), colour='#696969', leave=True):
    data = row.to_dict()
    playlists.insert_one(data)


# Get number of unique playlist_id
print(f'Number of unique playlist_id: {len(playlists.distinct("playlist_id"))}')

# Get number of unique owner_id
print(f'Number of unique owner_id: {len(playlists.distinct("owner_id"))}')