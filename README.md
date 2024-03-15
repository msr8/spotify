# Index
1) [Introduction](#1-introduction)
2) [Running the webserver](#2-running-the-webserver)
    1) [Running via docker](#21-running-via-docker)
    2) [Running via source](#22-running-via-source)



<br><hr><br>



# 1) Introduction




<br><hr><br>



# 2) Running the webserver

### 2.1) Running via docker

1) Pull the image from dockerhub
```bash
docker pull maybemsr8/spotify
```

2) Run the image
```bash
docker run -it -p 8000:8000 --name spotify-cont maybemsr8/spotify
```

Now you can access the webserver at `http://127.0.0.1:8000`. If you want to run the webserver again, you can use the following command:
```bash
docker start -i spotify-cont
```

<br>

### 2.2) Running via source

1) Clone the repository
```bash
git clone https://github.com/msr8/spotify
```

2) Install the requirements
```bash
#
```


<!-- https://www.kaggle.com/datasets/markmikaelson/7mil-spotify-audio-features/download?datasetVersionNumber=1 -->