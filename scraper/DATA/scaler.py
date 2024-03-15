from sklearn.preprocessing import MinMaxScaler
from pymongo import MongoClient

TO_SCALE = [
    'acousticness',
    'danceability',
    'energy',
    'instrumentalness',
    'liveness',
    'loudness',
    'speechiness',
    'tempo',
    'valence'
]

DB          = MongoClient('localhost', 27017)['spotify']
tracks_coll = DB['tracks']
print('Connected to tracks')


for i in TO_SCALE:
    # Get the max and min value
    pipeline = [
        {'$match': {i: {'$ne': None}}},
        {'$group': {
            '_id': None,
            'max': {'$max': f'${i}'},
            'min': {'$min': f'${i}'}
        }}
    ]
    min_max_val = list(tracks_coll.aggregate(pipeline))[0]
    min_val = min_max_val['min']
    max_val = min_max_val['max']
    print(f'{i}: {min_val} - {max_val}')

    # Initialize the scaler
    scaler = MinMaxScaler()
    scaler.fit([[min_val], [max_val]])

    # # Scale the values
    # pipeline = [
    #     {'$match': {i: {'$ne': None}}},
    #     {'$project': {
    #         'track_id': '$track_id',
    #         i: {'$arrayElemAt': [scaler.transform([[f'${i}']]), 0]}
    #     }}
    # ]


