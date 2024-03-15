from bs4 import BeautifulSoup
import requests as rq
from sty import fg

import datetime as dt
import time as t
import json


class RateLimited(Exception):
    pass



class Client:
    def __init__(self, client_id:str='', client_secret:str='', rate_limit_delay:int=30) -> None:
        self.rate_limit_delay   = rate_limit_delay
        self.client_id          = client_id
        self.client_secret      = client_secret
        self.auth_official      = ''
        self.auth_unofficial    = ''
        self.headers_official   = {'Authorization': f'Bearer {self.auth_official}'}
        self.headers_unofficial = {'authorization': f'Bearer {self.auth_unofficial}'}


    def get_ts(self, string=True, ts=None) -> str:
        # Gets the current time
        timezone_diff = dt.timedelta(hours=5.5)
        tz_info       = dt.timezone(timezone_diff, name="GMT")
        if not ts: curr_time = dt.datetime.now(tz_info)
        else:      curr_time = dt.datetime.fromtimestamp(ts, tz_info)
        if string: return curr_time.strftime('%d/%m/%y %H:%M:%S')
        else:      return curr_time.strftime('%d/%m/%y %H:%M:%S'), int(curr_time.timestamp())



    def generate_auth_official(self) -> None:
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_data = {
            'grant_type':    'client_credentials',
            'client_id':     self.client_id,
            'client_secret': self.client_secret,
        }
        r = rq.post(auth_url, data=auth_data).json()
        try:
            self.auth_official = r['access_token']
            self.headers_official['Authorization'] = f'Bearer {self.auth_official}'
        except KeyError:
            print(f'{fg.red}[{self.get_ts()}] KeyError while generating official auth, saving returned HTML in error.json{fg.rs}')
            print(self.client_id, self.client_secret)
            print('huh')
            with open('error.json', 'w') as f: json.dump(r, f, indent=4)
            exit()



    def generate_auth_unofficial(self) -> None:
        url  = 'https://open.spotify.com/'
        while True:
            r    = rq.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            tags = soup.find_all('script', id='session')
            # If desired number of tags found
            if len(tags) == 1: break
            # Elif no tags found and the HTML starts with "upstream"
            elif len(tags) == 0 and r.text.startswith('upstream'):
                print(f'{fg.yellow}[{self.get_ts()}] upstream error while generating unoffical auth, retrying after {self.rate_limit_delay}s{fg.rs}')
                t.sleep(self.rate_limit_delay)

        # If incossistent number of tags
        if len(tags) != 1:
            print(f'{fg.red}[{self.get_ts()}] Inconsistent number of tags, saving returned HTML in error.html{fg.rs}')
            with open('error.html', 'w') as f: f.write(r.text)
            exit()
        # Get the authtoken
        try:
            ret = json.loads(tags[0].contents[0])['accessToken']
        except Exception as e:
            print(f'{fg.red}[{self.get_ts()}] (Unknown error while generating unoffical auth) {e}, saving returned HTML in error.html{fg.rs}')
            with open('error.html', 'w') as f: f.write(r.text)
            exit()
        
        # Updates attributes
        self.auth_unofficial = ret
        self.headers_unofficial['authorization'] = f'Bearer {self.auth_unofficial}'



    def get_followers_of_user(self, user_id:str) -> list[dict]:
        '''
        - Some users (like 31jlm4tl7dsqtg353xiyzayzcupe, as of 3/12/23) do not have a name, so their json has the "name" key missing
        - Folks with 0 followers (like 31eywvs5uhunjkkq64ztgy4eg3vu) will have the "followers_count" key missing
        - At most 1000 followers are returned
        - Sometimes a 504 status code might be returned
        '''
        url = f'https://spclient.wg.spotify.com/user-profile-view/v3/profile/{user_id}/followers'
        while True:
            r = rq.get(url, headers=self.headers_unofficial)
            
            # Successful request
            if r.status_code == 200:
                try:
                    # Check if no followers. If no followers, return empty list
                    if not r.json(): return []
                    # Process & return data
                    return [{
                        'user_id':          x['uri'].split('spotify:user:')[-1],
                        'display_name':     x.get('name', None),
                        'followers_count':  x.get('followers_count', 0)
                    } for x in r.json()['profiles']]
                except KeyError: # If recieved JSON that didnt have the desired keys
                    print(f'{fg.red}[{self.get_ts()}] KeyError while getting followers of {user_id}, saving returned HTML in error.html{fg.rs}')
                    with open('error.html', 'w') as f: f.write(r.text)
                    exit()
            # Invalid/expired token
            elif r.status_code == 401:
                print(f'{fg.yellow}[{self.get_ts()}] 401 (Invalid/expired token) while getting followers of {user_id}, regenerating token{fg.rs}')
                self.generate_auth_unofficial()
            # Rate limited
            elif r.status_code == 429:
                print(f'{fg.red}[{self.get_ts()}] Rate limited while getting followers of {user_id}, waiting for {self.rate_limit_delay}s{fg.rs}')
                t.sleep(self.rate_limit_delay)
            # 504
            elif r.status_code == 504:
                print(f'{fg.red}[{self.get_ts()}] 504 (Gateway Timeout) while getting followers of {user_id}, trying again{fg.rs}')
            # Some other error
            else:
                print(f'{fg.red}[{self.get_ts()}] Status code {r.status_code} returned while getting followers of {user_id}, saving returned HTML in error.html{fg.rs}')
                with open('error.html', 'w') as f: f.write(r.text)
                exit()



    def get_playlists_of_user_unofficial(self, user_id:str) -> list[dict]:
        '''
        - Sometimes "owner_name" is a key of the data returned, sometimes its not, so not saving that
        - Sometimes image_url returns NaN
        - For playlists with 0 likes (like 0IPa404xeiXX8G44oKJNDl), "followers_count" is not a key of the data returned
        '''
        url = f'https://spclient.wg.spotify.com/user-profile-view/v3/profile/{user_id}/playlists'
        while True:
            try:
                r = rq.get(url, headers=self.headers_unofficial)
            except rq.exceptions.ConnectionError:
                print(f'{fg.red}[{self.get_ts()}] ConnectionError while getting playlists of {user_id}, waiting for {self.rate_limit_delay}s{fg.rs}')
                t.sleep(self.rate_limit_delay)
                continue
            
            # Successful request
            if r.status_code == 200:
                try:
                    # If no playlists, return an empty list
                    if not r.json(): return []
                    # Process & return data
                    return [{
                        'playlist_id':  x['uri'].split('spotify:playlist:')[-1],
                        'likes':        x.get('followers_count', 0),
                        'owner_id':     x['owner_uri'].split('spotify:user:')[-1],
                    } for x in r.json()['public_playlists'] if x['owner_uri'].split('spotify:user:')[-1] == user_id]
                except KeyError: # If recieved JSON that didnt have the desired keys
                    print(f'{fg.red}[{self.get_ts()}] KeyError while getting playlists of {user_id}, saving returned HTML in error.html{fg.rs}')
                    with open('error.html', 'w') as f: f.write(r.text)
                    exit()
            # Invalid/expired token
            elif r.status_code == 401:
                print(f'{fg.yellow}[{self.get_ts()}] 401 (Invalid/expired token) while getting playlists of {user_id}, regenerating token{fg.rs}')
                self.generate_auth_unofficial()
            # Rate limited
            elif r.status_code == 429:
                print(f'{fg.red}[{self.get_ts()}] Rate limited while getting playlists of {user_id}, waiting for {self.rate_limit_delay}s{fg.rs}')
                t.sleep(self.rate_limit_delay)
            # 502 (Bad Gateway)
            elif r.status_code == 502:
                print(f'{fg.red}[{self.get_ts()}] 502 (Bad Gateway) while getting playlists of {user_id}, trying again{fg.rs}')
            # Some other error
            else:
                print(f'{fg.red}[{self.get_ts()}] Status code {r.status_code} returned while getting playlists of {user_id}, saving returned HTML in error.html{fg.rs}')
                with open('error.html', 'w') as f: f.write(r.text)
                exit()



    def get_tracks_in_playlist_official(self, playlist_id:str) -> list[str]:
        '''
        - For items that are not tracks, the value of the "track" key is None/null, like in playlist 01GGueGryJFkJvS52qPdZj
        - Sometimes, even when the track is not null, its id can be null for some reason
        - The rate limit here is extreme, its like only a few thousand per DAY
        '''
        ret = []

        count = 0
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        while True:
            try:
                r = rq.get(url, headers=self.headers_official)
                count += 1
            except rq.exceptions.ConnectionError:
                print(f'{fg.red}[{self.get_ts()}] ConnectionError while getting tracks of {playlist_id}, waiting for {self.rate_limit_delay}s ({count}){fg.rs}')
                t.sleep(self.rate_limit_delay)
                continue
            
            # Successful request
            if r.status_code == 200:
                try:
                    # Process data and append it to ret
                    ret.extend([ i['track']['id'] for i in r.json()['items'] if i['track'] and i['track']['id'] ])
                    # Update the url
                    url = r.json()['next']
                    # If no more tracks, return
                    if not url: return ret
                except KeyError: # If recieved JSON that didnt have the desired keys
                    print(f'{fg.red}[{self.get_ts()}] KeyError while getting tracks of {playlist_id}, saving returned HTML in error.html ({count}){fg.rs}')
                    with open('error.html', 'w') as f: f.write(r.text)
                    exit()
            # Invalid/expired token
            elif r.status_code == 401:
                print(f'{fg.yellow}[{self.get_ts()}] 401 (Invalid/expired token) while getting tracks of {playlist_id}, regenerating token ({count}){fg.rs}')
                self.generate_auth_official()
            # 400 ("Only valid bearer authentication supported")
            elif r.status_code == 400:
                print(f'{fg.red}[{self.get_ts()}] 400 while getting tracks of {playlist_id}, regenerating token ({count}){fg.rs}')
                self.generate_auth_official()
            # 429 (Rate limited)
            elif r.status_code == 429:
                retry_after = int(r.headers['Retry-After'])
                ts_str, ts_int = self.get_ts(string=False)
                print(f'{fg.red}[{ts_str}] Rate limited while getting tracks of {playlist_id}, retrying after {retry_after}s, ie ({self.get_ts(ts=ts_int+retry_after)}) ({count}){fg.rs}')
                t.sleep(retry_after)
            # 404, means playlist doesnt exist (anymore)
            elif r.status_code == 404:
                print(f'{fg.red}[{self.get_ts()}] 404 while getting tracks of {playlist_id}, skipping ({count}){fg.rs}')
                return []
            # 500 (Server Error)
            elif r.status_code == 500:
                print(f'{fg.red}[{self.get_ts()}] 500 (Server Error) while getting tracks of {playlist_id}, trying again ({count}){fg.rs}')
            # 502 (Bad Gateway)
            elif r.status_code == 502:
                print(f'{fg.red}[{self.get_ts()}] 502 (Bad Gateway) while getting tracks of {playlist_id}, trying again ({count}){fg.rs}')
            # Some other error
            else:
                print(f'{fg.red}[{self.get_ts()}] Status code {r.status_code} returned while getting tracks of {playlist_id}, saving returned HTML in error.html ({count}){fg.rs}')
                with open('error.html', 'w') as f: f.write(r.text)
                exit()
    


    def get_tracks_in_playlist_unofficial(self, playlist_id:str) -> list[str]:
        '''
        - The limit seems can be max 370, because when I do 371 I get the error message "maximum query complexity exceeded 70121 > 70000"
        - r.json()['data']['playlistV2']['content']['totalCount'] is the total number of ITEMS (not tracks) in the playlist
        - Sometimes there can be an error but the status code will still be 200. In such cases, r.json()['data']['playlistV2']['__typename'] will be "GenericError"
        - Also have literally never been rate limited when doing these queries
        '''
        variables_template = '{"uri":"spotify:playlist:'+playlist_id+'", "limit":370, "offset":%%OFFSET%%}'
        url      = 'https://api-partner.spotify.com/pathfinder/v1/query'
        get_data = {
            'operationName': 'fetchPlaylistContents',
            'variables':     variables_template.replace('%%OFFSET%%', '0'),
            'extensions':    '{"persistedQuery":{"version":1,"sha256Hash":"fe3a70ec6e06afe98c22b3421bd4914d10e9432ff514c2efc79cf0262b5e2e0b"}}'
        }
        
        ret    = []
        count  = 0
        offset = 0

        while True:
            try:
                r = rq.get(url, headers=self.headers_unofficial, params=get_data)
                count += 1
            except rq.exceptions.ConnectionError:
                print(f'{fg.red}[{self.get_ts()}] ConnectionError while getting tracks of {playlist_id}, waiting for {self.rate_limit_delay}s ({count}){fg.rs}')
                t.sleep(self.rate_limit_delay)
                continue
            
            # Successful request
            if r.status_code == 200:
                try:
                    # Check if playlist not found
                    if r.json()['data']['playlistV2']['__typename'] == 'NotFound':
                        # print(f'{fg.red}[{self.get_ts()}] Playlist {playlist_id} not found, skipping ({count}){fg.rs}')
                        return []
                    # Check if some error occured (Must do it after cause the content key is not present in non-existing playlists)
                    if r.json()['data']['playlistV2']['__typename'] == 'GenericError' or r.json()['data']['playlistV2']['content']['__typename'] == 'GenericError':
                        print(f'{fg.red}[{self.get_ts()}] GenericError while getting tracks of {playlist_id}, retrying after {self.rate_limit_delay}s ({count}){fg.rs}')
                        t.sleep(self.rate_limit_delay)
                        continue
                    # Process data and append it to ret
                    ret.extend([ i['itemV2']['data']['uri'].split(':')[-1] for i in r.json()['data']['playlistV2']['content']['items'] if i['itemV2']['data']['__typename']=='Track' ])
                    # Update the offset
                    offset += 370
                    get_data['variables'] = variables_template.replace('%%OFFSET%%', str(offset))
                    # If no more tracks, return
                    if offset >= r.json()['data']['playlistV2']['content']['totalCount']: return ret
                except KeyError:
                    print(f'{fg.red}[{self.get_ts()}] KeyError while getting tracks of {playlist_id}, saving returned JSON in error.json ({count}){fg.rs}')
                    with open('error.json', 'w') as f: f.write(r.text)
                    exit()
                # TypeError: 'NoneType' object is not subscriptable (it sometimes happens randomly, not sure what JSON is returned to cuase that)
                except TypeError:
                    print(f'{fg.red}[{self.get_ts()}] TypeError while getting tracks of {playlist_id}, saving returned JSON in error.json and retrying ({count}){fg.rs}')
                    with open('error.json', 'w') as f: f.write(r.text)
                    continue

            # Invalid/expired token
            elif r.status_code == 401:
                print(f'{fg.yellow}[{self.get_ts()}] 401 (Invalid/expired token) while getting tracks of {playlist_id}, regenerating token ({count}){fg.rs}')
                self.generate_auth_unofficial()
            # 429 (Rate limited)
            elif r.status_code == 429:
                retry_after = int(r.headers['Retry-After'])
                ts_str, ts_int = self.get_ts(string=False)
                print(f'{fg.red}[{ts_str}] Rate limited while getting tracks of {playlist_id}, retrying after {retry_after}s, ie ({self.get_ts(ts=ts_int+retry_after)}) ({count}){fg.rs}')
                t.sleep(retry_after)
            # 500 (Server Error)
            elif r.status_code == 500:
                print(f'{fg.red}[{self.get_ts()}] 500 (Server Error) while getting tracks of {playlist_id}, trying again ({count}){fg.rs}')
            # 502 (Bad Gateway)
            elif r.status_code == 502:
                print(f'{fg.red}[{self.get_ts()}] 502 (Bad Gateway) while getting tracks of {playlist_id}, trying again ({count}){fg.rs}')
            # 503 (Service Unavailable)
            elif r.status_code == 503:
                print(f'{fg.red}[{self.get_ts()}] 503 (Service Unavailable) while getting tracks of {playlist_id}, trying again after {self.rate_limit_delay}s ({count}){fg.rs}')
                t.sleep(self.rate_limit_delay)
            # 504 (Gateway Timeout)
            elif r.status_code == 504:
                print(f'{fg.red}[{self.get_ts()}] 504 (Gateway Timeout) while getting tracks of {playlist_id}, trying again ({count}){fg.rs}')
            # Some other error
            else:
                print(f'{fg.red}[{self.get_ts()}] Status code {r.status_code} returned while getting tracks of {playlist_id}, saving returned HTML in error.html ({count}){fg.rs}')
                with open('error.html', 'w') as f: f.write(r.text)
                exit()





    def get_tracks_features_official(self, track_ids:list[str]) -> list[dict]:
        '''
        - For deleted/unavailable songs, the "list" will just be None
        - Cap of 2k reqs per day
        '''
        # Check if more than 100 track_ids were passed
        if len(track_ids) > 100:
            print(f'{fg.red}[{self.get_ts()}] More than 100 track_ids passed to get_tracks_features_official, saving track_ids in error.json{fg.rs}')
            with open('error.json', 'w') as f: json.dump(track_ids, f, indent=4)
            exit()
        
        url = f'https://api.spotify.com/v1/audio-features?ids={",".join(track_ids)}'

        while True:
            try:
                r = rq.get(url, headers=self.headers_official)
            except rq.exceptions.ConnectionError:
                print(f'{fg.red}[{self.get_ts()}] ConnectionError while getting tracks features, waiting for {self.rate_limit_delay}s{fg.rs}')
                t.sleep(self.rate_limit_delay)
                continue
            
            # Successful request
            if r.status_code == 200:
                try:
                    # Process data and return it
                    return [{
                        'track_id':         x['id'],
                        'danceability':     x['danceability'],
                        'energy':           x['energy'],
                        'key':              x['key'],
                        'loudness':         x['loudness'],
                        'mode':             x['mode'],
                        'speechiness':      x['speechiness'],
                        'acousticness':     x['acousticness'],
                        'instrumentalness': x['instrumentalness'],
                        'liveness':         x['liveness'],
                        'valence':          x['valence'],
                        'tempo':            x['tempo'],
                        'duration_ms':      x['duration_ms'],
                        'time_signature':   x['time_signature'],
                    } for x in r.json()['audio_features'] if x]
                except KeyError:
                    print(f'{fg.red}[{self.get_ts()}] KeyError while getting tracks features, saving returned JSON in error.json{fg.rs}')
                    with open('error.json', 'w') as f: f.write(r.text)
                    exit()
            # Invalid/expired token
            elif r.status_code == 401:
                print(f'{fg.yellow}[{self.get_ts()}] 401 (Invalid/expired token) while getting tracks features, regenerating token{fg.rs}')
                self.generate_auth_official()
            # 400 ("Only valid bearer authentication supported")
            elif r.status_code == 400:
                print(f'{fg.red}[{self.get_ts()}] 400 while getting tracks features, regenerating token{fg.rs}')
                self.generate_auth_official()
            # 429 (Rate limited)
            elif r.status_code == 429:
                # For some reason the response here doesnt have a Retry-After header
                # print(f'{fg.red}[{self.get_ts()}] Rate limited while getting tracks features, so exiting{fg.rs}')
                # exit()
                raise RateLimited('Rate limited while getting tracks features')
            # 500 (Server Error)
            elif r.status_code == 500:
                print(f'{fg.red}[{self.get_ts()}] 500 (Server Error) while getting tracks features, trying again{fg.rs}')
            # 502 (Bad Gateway)
            elif r.status_code == 502:
                print(f'{fg.red}[{self.get_ts()}] 502 (Bad Gateway) while getting tracks features, trying again{fg.rs}')
            # 503 (Service Unavailable)
            elif r.status_code == 503:
                print(f'{fg.red}[{self.get_ts()}] 503 (Service Unavailable) while getting tracks features, trying again after {self.rate_limit_delay}s{fg.rs}')
                t.sleep(self.rate_limit_delay)
            # Some other error
            else:
                print(f'{fg.red}[{self.get_ts()}] Status code {r.status_code} returned while getting tracks features, saving returned HTML in error.html{fg.rs}')
                with open('error.html', 'w') as f: f.write(r.text)
                exit()





