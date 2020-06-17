# For required Python packages, use requirements.txt

# For required system packages, see following (only tested for Ubuntu 20.04, google for other OS')
## Install Tor ([source](https://www.linuxuprising.com/2018/10/how-to-install-and-use-tor-as-proxy-in.html))
### Install apt transport
```
sudo apt install apt-transport-https curl
```
### Insert Tor key to apt
```
sudo -i
echo "deb https://deb.torproject.org/torproject.org/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/tor.list
curl https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --import
gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | apt-key add -
apt update
exit
```
### Install Tor packages
```
sudo apt install tor tor-geoipdb torsocks deb.torproject.org-keyring
```
### Set `ControlPort` variable for Tor. In here "mypassword" is used as an example password
```
service tor stop
echo "ControlPort 9051" >> /etc/tor/torrc
echo HashedControlPassword $(tor --hash-password "mypassword" | tail -n 1) >> /etc/tor/torrc
tail -n 2 /etc/tor/torrc
service tor start
```
### Check if Tor is running
```
service tor status
```
### Check if you have a different IP with Tor
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

## Install Privoxy ([source](https://www.linuxuprising.com/2018/10/how-to-install-and-use-tor-as-proxy-in.html))
```
sudo apt install privoxy
```
### Route HTTP/HTTPS traffice through Tor using Privoxy
```
service privoxy start
echo "forward-socks5t / 127.0.0.1:9050 ." >> /etc/privoxy/config
service privoxy start
```
### Check if Privoxy is running
```
service privoxy status
```
### Check if you have a different IP with Privoxy now
```
curl -x 127.0.0.1:8118 http://icanhazip.com/
```

## Docker
Pull the torproxy image
```
docker pull dperson/torproxy
```

Run the image, circuit age to be reused is at max = 60 seconds (TOR_MaxCircuitDirtiness), attempt to change circuit every 10 seconds (TOR_NewCircuitPeriod)
```
docker run -it -p 8118:8118 -p 9050:9050 --env TOR_NewCircuitPeriod=10 --env TOR_MaxCircuitDirtiness=60 -d dperson/torproxy
```

           