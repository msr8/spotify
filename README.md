<div align="center">

<!-- https://coolors.co/gradient-palette/f72585-066da5?number=5 -->

[![GitHub stars](https://img.shields.io/github/stars/msr8/spotify?color=F72585&labelColor=302D41&style=for-the-badge)](https://github.com/msr8/spotify)
[![GitHub last commit](https://img.shields.io/github/last-commit/msr8/spotify?color=BB378D&labelColor=302D41&style=for-the-badge)](https://github.com/msr8/spotify)
[![GitHub issues](https://img.shields.io/github/issues/msr8/spotify?color=7F4995&labelColor=302D41&style=for-the-badge)](https://github.com/msr8/spotify)
[![Docker Image Size](https://img.shields.io/docker/image-size/maybemsr8/spotify?color=425B9D&labelColor=302D41&style=for-the-badge&label=Docker%20Image%20Size)](https://hub.docker.com/r/maybemsr8/spotify)
[![Docker Pulls](https://img.shields.io/docker/pulls/maybemsr8/spotify?color=066DA5&labelColor=302D41&style=for-the-badge)](https://hub.docker.com/r/maybemsr8/spotify)


![1-img](screenshots/1.png)
![2-img](screenshots/2.png)
![3-img](screenshots/3.png)
![4-img](screenshots/4.png)

</div>



This project consists of two parts:

1) **Scraper:** A scraper whose working has 4 phases/parts:
    1) Scrapes all the followers of the last scraped followers of a given user, and stores it in the `users` collection *(unoffical reverse-engineered API)*
    2) Scrapes all the playlists of all the users, and stores it in the `playlists` collection *(unoffical reverse-engineered API)*
    3) Scrapes the IDs of all the tracks of all the playlists, and stores it in `DATA/playlists_whose_tracks_have_been_scraped.txt` *(unoffical reverse-engineered API)*
    4) Scrapes the audio features of all the tracks, and stores it in the `tracks` collection *(official API)*
2) **Webserver:** A webserver hosting a webpage that shows recommendations based on the song whose link/ID is provided by the user. The recommendations are based on the audio features of the song, and are calculated using a custom optimised K-Nearest Neighbours algorithm



<br><hr><br>



# Index
1) [Introduction](#1-introduction)
2) [Running the webserver](#2-running-the-webserver)
    1) [Running via docker (recommended)](#21-running-via-docker-recommended)
    2) [Running via source](#22-running-via-source)
3) [Information about the data collected](#3-information-about-the-data-collected)




<br><hr><br>



# 1) Introduction
Developed a spotify scraper and a corresponding website enabling users to receive personalized recommendations based on Spotify track links or IDs

<br>

Some features of the scraper:
- Leveraged the Spotify API to scrape the audio features of over 7 million songs
- Implemented robust error handling within the scraper as to prevent interruptions due to errors during operation, thereby ensuring continuous operation over extended durations without interruptions
- Demonstrated adeptness in utilizing both, official and unofficial APIs for data acquisition
- Organized scraping functionalities within a unified `Client` class, streamlining operations via a single object
- Employed batch processing for file and data operations within the scraper, optimizing performance by mitigating I/O bottlenecks

<br>

Some features of the webserver:
- Utilized a custom optimized K-Nearest Neighbors algorithm for recommendation generation
- Implemented MongoDB as the database backend for efficient data storage and flexible querying capabilities
- Containerized the web server using Docker for seamless deployment and execution across diverse environments
- Implemented extensive and thorough error handling
- Designed a minimalist yet responsive frontend interface, prioritizing usability and simplicity without unnecessary clutter

<br>

Technologies & Languages used:
- Django
- MongoDB
- Docker
- Spotify API
- Python
- HTML
- CSS
- JavaScript



<br><hr><br>



# 2) Running the webserver

### 2.1) Running via docker (recommended)
**Pre-requisites:** [Docker Engine](https://docs.docker.com/engine/install/) should be installed and running

1) Pull the image from dockerhub
```bash
docker pull maybemsr8/spotify
```

2) Run the image
```bash
docker run -it -p 8000:8000 --name spotify-cont maybemsr8/spotify
```

Give it a minute to initialise everything and then you can access the webserver at `http://127.0.0.1:8000`. If you want to run the webserver again, you can use the following command:
```bash
docker start -i spotify-cont
```

<br>

### 2.2) Running via source
**Pre-requisites:** Latest version of [python](https://www.python.org/downloads/) should be installed. [MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/) should be installed and running on port 27018. If you want to use MongoDB on another port, modify the `PORT` variable in [`webserver/backend/views.py`](webserver/backend/views.py) to the port you want to use

1) Clone the repository and cd into it
```bash
git clone https://github.com/msr8/spotify
cd spotify
```

2) Import the data into MongoDB
```bash
mongoimport --db spotify --collection tracks --type csv --file DATA/tracks.csv --headerline
```

3) cd into the webserver and install the python requirements
```bash
cd webserver
python -m pip install -r requirements.txt
```

4) Run the webserver
```bash
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
```

Give it a minute to initialise everything and then you can access the webserver at `http://127.0.0.1:8000`. To run the webserver again, you can use the following commands:
```bash
# cd into the directory containing the code
cd spotify/webserver
python manage.py runserver 0.0.0.0:8000
```



<br><hr><br>



# 3) Information about the data collected
Total records: 7,458,293

<br>

### Columns:

(For more information, see [Spotify's official documentation](https://developer.spotify.com/documentation/web-api/reference/get-audio-features))

| Column Name      | Datatype | Description |
|------------------|----------|-------------|
| _id              | string   | Track ID of the song |
| acousticness     | float    | A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic |
| danceability     | float    | Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable |
| duration_ms      | int      | The duration of the track in milliseconds |
| energy           | float    | Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy |
| instrumentalness | float    | Predicts whether a track contains no vocals. "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0 |
| key              | int      | The key the track is in. Integers map to pitches using standard Pitch Class notation. E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on. If no key was detected, the value is -1 |
| liveness         | float    | Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live |
| loudness         | float    | The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typically range between -60 and 0 db |
| mode             | int      | Mode indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived. Major is represented by 1 and minor is 0 |
| speechiness      | float    | Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks |
| tempo            | float    | The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration |
| time_signature   | int      | An estimated time signature. The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7 indicating time signatures of "3/4", to "7/4" |
| valence          | float    |  A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry) |


<!--

https://www.kaggle.com/datasets/markmikaelson/7mil-spotify-audio-features/download?datasetVersionNumber=1 

docker build --tag spotify-image --file webserver/Dockerfile .
docker image tag spotify-image maybemsr8/spotify
docker image push maybemsr8/spotify

-->