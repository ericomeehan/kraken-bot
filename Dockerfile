FROM debian
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install --break-system-packages krakenex pykrakenapi python-dotenv scipy
COPY . /usr/local/src/kraken-bot
