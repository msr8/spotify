from tqdm import tqdm

import os


BATCH_SIZE = 1000

TRACK_IDS_FP  = 'DATA/track_ids.txt'
TRACK_IDS_DIR = 'DATA/TRACK_IDS'


with open(TRACK_IDS_FP, 'r') as f:
    track_ids = set(f.read().split('\n'))
orig_len = len(track_ids)


for fn_ext in tqdm(os.listdir(TRACK_IDS_DIR), colour='#696969', leave=True):
    if     fn_ext.startswith('.'):  continue
    if not fn_ext.endswith('.txt'): continue

    fp = os.path.join(TRACK_IDS_DIR, fn_ext)
    with open(fp) as f:
        new_data = set(f.readlines())
    track_ids.update(new_data)


if '' in track_ids: track_ids.remove('')
with open(TRACK_IDS_FP, 'w') as f:
    f.write('\n'.join(track_ids))


print(f'Saved {len(track_ids)-orig_len} new track_ids, totalling to {len(track_ids)} track_ids')