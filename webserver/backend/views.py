from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from rest_framework.request import Request
from pymongo import MongoClient
from pymongo.collection import Collection
from sty import fg, ef

from time import perf_counter
from json import JSONDecodeError, loads as json_loads


DB_NAME         = 'spotify'
COLLECTION_NAME = 'tracks'
# DB_NAME         = 'test'
# COLLECTION_NAME = 'tracks_test'
PORT            = 27018





def func_get_nearest_tracks(tracks:Collection, track_info:dict[str,float], max_diff:float=0.05, limit:int=30) -> list[str]:
    features = [
        'danceability',
        'acousticness',
        'energy',
        'instrumentalness',
        'liveness',
        'speechiness',
    ]

    bounds = { i : {
        'lower': max(track_info[i]-max_diff, 0),
        'upper': min(track_info[i]+max_diff, 1)
    } for i in features }


    diffs = [{'$abs': { '$subtract': [
        f'${i}',
        track_info[i]
    ]}} for i in features ]

    projection = { i: 1 for i in features }
    projection['distance'] = 1
    projection['diff']     = 1


    # Filter out tracks that are not in the range or if any of the features are None,
    step_1 = { '$match': {
        i: {'$gte': bounds[i]['lower'], '$lte': bounds[i]['upper'], '$ne': None}
    for i in features }}

    # Calculate the euclidean distance
    step_2 = { '$addFields': { 'distance': { '$sqrt': { '$sum': diffs }},
    'diff': diffs
    }}

    # Remove any duplicates of the original song we might have. For some reason doing this in step_1 takes like 6x longer
    step_3 = { '$match': {'distance': {'$ne':0} } }
    # Sort
    step_4 = { '$sort': { 'distance': 1 }}
    # Projection
    step_5 = { '$project': projection }
    # Limit
    step_6 = { '$limit': limit }

    pipeline = [
        step_1,
        step_2,
        step_3,
        step_4,
        step_5,
        step_6,
    ]

    result = [{'track_id':i['_id'] , 'distance':i['distance']} for i in tracks.aggregate(pipeline)]
    return result



    







def node_test(request: HttpRequest) -> JsonResponse:
    get_data = request.GET.dict()
    return JsonResponse({'GET': get_data, 'oky':'haha'})


def node_get_track_id(request: HttpRequest) -> JsonResponse:
    '''
    https://open.spotify.com/track/6161
    6161 (ie just the track ID)
    '''
    # Get the track url from the body
    try:
        track_url:str = json_loads(request.body)['track_url']
    except JSONDecodeError:
        return JsonResponse({'status':1541, 'message':ERROR_CODES[1541].format(body_content=request.body)})
    except KeyError:
        return JsonResponse({'status':1542, 'message':ERROR_CODES[1542]})
    
    # Process the track_url
    try:
        # If there is no http, meaning its just the track ID
        if 'http' not in track_url:
            track_id = track_url
        # If there is http or https, meaning its the full url
        else:
            track_id = track_url.split('track/')[-1].split('?')[0]
        
        return JsonResponse({'status':200, 'track_id':track_id})
    except IndexError:
        return JsonResponse({'status':1543, 'message':ERROR_CODES[1543]})

    

def node_get_nearest_tracks(request: HttpRequest) -> JsonResponse:
    track_id = request.GET.get('track_id', request.POST.get('track_id'))

    if not track_id:
        try: 
            track_id:str = json_loads(request.body)['track_id']   
        except JSONDecodeError:
            return JsonResponse({'status':1541, 'message':ERROR_CODES[1541].format(body_content=request.body)})
        except KeyError:
            return JsonResponse({'status':1544, 'message':ERROR_CODES[1544]})

    # If no track id was provided
    if not track_id: return JsonResponse({'status':1544, 'message':ERROR_CODES[1544]})

    # Get the track info
    track_info = tracks.find_one({'_id': track_id})

    # If the track does not exist in our database
    if not track_info: return JsonResponse({'status':1545, 'message':ERROR_CODES[1545]})

    nearest_tracks = func_get_nearest_tracks(tracks, track_info)
    return JsonResponse({'status':200, 'data':nearest_tracks})






ERROR_CODES = {
    1541: 'Invalid JSON in body ({body_content})',
    1542: 'No track URL provided',
    1543: 'Invalid track URL',
    1544: 'No track ID provided',
    1545: 'Track does not exist in the database',
}

db     = MongoClient('localhost', PORT)[DB_NAME]
tracks = db[COLLECTION_NAME]
print(f'{fg(0,255,0)}{ef.bold}MongoDB connection established!{fg.rs}{ef.rs}')

# Gotta do flush=True because of docker containers
print(f'{fg(0,255,0)}Initialising cache in MongoDB database...{fg.rs}', flush=True)
start   = perf_counter()
req     = HttpRequest()
req.GET = {'track_id': '1N8TTK1Uoy7UvQNUazfUt5'}
node_get_nearest_tracks(req)
end     = perf_counter()
print(f'{fg(0,255,0)}Done {fg(0,155,0)}({int(end-start)}s){fg.rs}', flush=True)
