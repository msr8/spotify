from dotenv import load_dotenv
from os import getenv as env

load_dotenv()
CREDS = (
    (env('CLIENT_ID_1'), env('CLIENT_SEC_1')),
    (env('CLIENT_ID_2'), env('CLIENT_SEC_2')),
    (env('CLIENT_ID_3'), env('CLIENT_SEC_3')),
    (env('CLIENT_ID_4'), env('CLIENT_SEC_4')),
    (env('CLIENT_ID_5'), env('CLIENT_SEC_5')),
    (env('CLIENT_ID_6'), env('CLIENT_SEC_6')),
    (env('CLIENT_ID_7'), env('CLIENT_SEC_7')),
)