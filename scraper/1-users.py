from base import Client
from pymongo import MongoClient
from tqdm import tqdm

import datetime as dt

TARGET_DEPTH = 3
BATCH_SIZE   = 100



mongo_cl  = MongoClient('localhost', 27017)
print('Connection to MongoDB established')
db        = mongo_cl['spotify']
users     = db['users']
cl        = Client('','')

max_depth = int(users.find_one(sort=[('depth', -1)])['depth'])
print(f'Max depth: {max_depth}')
already_scraped = set(users.distinct('user_id'))
already_gotten_followers = set(users.distinct('source'))


count = 0
data = []
while max_depth < TARGET_DEPTH:
    max_depth_users = [i['user_id'] for i in users.find({'depth': max_depth}, {'_id': 0, 'user_id': 1})]
    max_depth += 1

    data = []
    for user_id in tqdm(max_depth_users, colour='#696969', desc=f'{max_depth}', leave=True):
        # If we have already scraped followers of this user, skip
        if user_id in already_gotten_followers: continue
        
        # Gets his followers
        new_data = cl.get_followers_of_user(user_id)
        for i in new_data.copy():
            if i['user_id'] in already_scraped: new_data.remove(i)
            else:                               already_scraped.add(i['user_id'])
        # Adds time when scraped, source, and depth to all dicts inside the list
        tz_info   = dt.timezone(dt.timedelta(hours=5.5))
        timestamp = dt.datetime.now(tz=tz_info)
        posix     = int(timestamp.timestamp())
        for i in new_data:
            i['time_scraped_posix'] = posix
            i['source'] = user_id
            i['depth']  = max_depth

        # Appends to `data`
        data.extend(new_data)

        # Save our data every BATCH_SIZE iterations
        count += 1
        if count >= BATCH_SIZE:
            users.insert_many(data)
            data.clear()
            count = 0
    
    # Save the data again, for the last incomplete batch
    users.insert_many(data)


# while max_depth+1 < TARGET_DEPTH:
#     max_depth    = int(df['depth'].max())
#     max_depth_df = df[df['depth'] == max_depth]

#     for user_id in tqdm(max_depth_df['user_id'], colour='#696969', desc=f'{max_depth}', leave=True):
#         # print(f'({max_depth}) Getting followers of {user_id}')
        
#         # Gets his followers
#         new_df = cl.get_followers_of_user(user_id)
#         # Adds url
#         new_df['url'] = new_df['user_id'].apply(lambda x: f'https://open.spotify.com/user/{x}')
#         # Adds time when scraped
#         tz_info   = dt.timezone(dt.timedelta(hours=5.5))
#         timestamp = dt.datetime.now(tz=tz_info)
#         new_df['time_scraped_posix']    = int(timestamp.timestamp())
#         # Adds source
#         new_df['source'] = user_id
#         # Adds depth
#         new_df['depth'] = max_depth + 1

#         # Appends to the main df (ignores the already existing user_ids)
#         filtered_df = new_df[~new_df['user_id'].isin(df['user_id'])]
#         df          = pd.concat([df, filtered_df], ignore_index=True)
#         # Saves our progress
#         df.to_csv('users.csv', index=False)
    





# df.to_csv(CSV_FP, index=False)
