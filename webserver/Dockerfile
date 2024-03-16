FROM python:3.12.2-bullseye

COPY webserver /webserver
COPY DATA /DATA

# Install mongoDB (https://www.mongodb.com/docs/v5.0/tutorial/install-mongodb-on-debian/)
RUN apt-get install gnupg curl
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-5.0.asc | gpg -o /usr/share/keyrings/mongodb-server-5.0.gpg --dearmor
RUN echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-5.0.gpg] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list
RUN apt-get update
RUN apt-get install -y mongodb-org
# Import our data
RUN mkdir /mongodb-database
RUN mongod --fork --logpath /var/log/mongod.log -dbpath /mongodb-database \
 && mongoimport --db spotify --collection tracks --type csv --file /DATA/tracks.csv --headerline

# Install python packages
RUN python -m pip install -r /webserver/requirements.txt

# Runtime
EXPOSE 8000
# Gotta use port 27018 cause of the error ""Failed to unlink socket file","attr":{"path":"/tmp/mongodb-27017.sock","error":"No such device or address"}"
# Gotta do "PYTHONBUFFERED=1" cz https://stackoverflow.com/a/31796350
# Gotta do 0.0.0.0:8000 cz https://stackoverflow.com/a/49476339
# This warning is there when doing mongosh in the container (via a bash conenction) "This server is bound to localhost. Remote systems will be unable to connect to this server. Start the server with --bind_ip <address> to specify which IP addresses it should serve responses from, or with --bind_ip_all to bind to all interfaces"
ENV PYTHONBUFFERED=1
WORKDIR /webserver
CMD ["/bin/sh" , "-c", "mongod --logpath /var/log/mongod.log --dbpath /mongodb-database --port 27018 --fork \
                     && echo '\\n\\033[1;95m[STARTING THE PYTHON PROGRAM]\\033[0m\\n' \
                     && python manage.py collectstatic --noinput \
                     && python manage.py runserver 0.0.0.0:8000"]
