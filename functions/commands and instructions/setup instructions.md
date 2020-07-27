# SSH to Ubuntu Server and do what you need below
```
ssh root@45.77.5.33 -L9200:localhost:9200 -L5601:localhost:5601
```
Preferably you can just skip to the Docker section to avoid playing around with the setup.


# Docker

## Running with docker-compose
Change dir to the root folder of this project
```
chmod 755 ./run.sh
```
Run that file
```
./run.sh
```

## Running manually
### Pull the torproxy image
```
docker pull dperson/torproxy
docker pull redis
docker pull python:3.7.7-slim-buster
```

### Run the following containers
```
docker run -d -p 6379:6379 --rm --net fad --name fad-redis redis

docker run -it -d -p 8118:8118 -p 9050:9050 --rm --net fad --name torproxy --env TOR_NewCircuitPeriod=10 --env TOR_MaxCircuitDirtiness=60 dperson/torproxy

docker run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" --rm --net fad --name elasticsearch docker.elastic.co/elasticsearch/elasticsearch:7.7.1

docker run -d -p 5601:5601 --rm --net fad --link elasticsearch:elasticsearch docker.elastic.co/kibana/kibana:7.7.1
```
Note that Tor circuit age to be reused is at max = 60 seconds (`TOR_MaxCircuitDirtiness`), attempt to change circuit every 10 seconds (`TOR_NewCircuitPeriod`).


### If you want to investigate Redis...
```
docker run -it --rm --net fad redis redis-cli -h fad-redis
```


# In case you want to mess with the setup

For required Python packages, use `requirements.txt`

For required system packages, see following (only tested for Ubuntu 20.04, google for other OS')
### Install Tor ([source](https://www.linuxuprising.com/2018/10/how-to-install-and-use-tor-as-proxy-in.html))
#### Install apt transport
```
sudo apt install apt-transport-https curl
```
#### Insert Tor key to apt
```
sudo -i
echo "deb https://deb.torproject.org/torproject.org/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/tor.list
curl https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --import
gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | apt-key add -
apt update
exit
```
#### Install Tor packages
```
sudo apt install tor tor-geoipdb torsocks deb.torproject.org-keyring
```
#### Set `ControlPort` variable for Tor. In here "mypassword" is used as an example password
```
service tor stop
echo "ControlPort 9051" >> /etc/tor/torrc
echo HashedControlPassword $(tor --hash-password "mypassword" | tail -n 1) >> /etc/tor/torrc
tail -n 2 /etc/tor/torrc
service tor start
```
#### Check if Tor is running
```
service tor status
```
#### Check if you have a different IP with Tor
For your original IP (2 ways):
```
curl http://icanhazip.com/
wget -qO - https://api.ipify.org; echo
```
For your Tor IP (2 ways):
```
torify curl http://icanhazip.com/
torsocks wget -qO - https://api.ipify.org; echo
```

### Install Privoxy after having Tor ([source](https://www.linuxuprising.com/2018/10/how-to-install-and-use-tor-as-proxy-in.html))
```
sudo apt install privoxy
```
#### Route HTTP/HTTPS traffice through Tor using Privoxy
```
service privoxy start
echo "forward-socks5t / 127.0.0.1:9050 ." >> /etc/privoxy/config
service privoxy start
```
#### Check if Privoxy is running
```
service privoxy status
```
#### Check if you have a different IP with Privoxy now
```
curl -x 127.0.0.1:8118 http://icanhazip.com/
curl -x 0.0.0.0:8118 http://icanhazip.com/
```
