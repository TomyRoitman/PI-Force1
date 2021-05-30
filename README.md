# PI-Force1
Autonomous car and tank system designed for raspberry pi.

##Server on RaspberryPI:

Install python requirements:
```
pip3 install -r requirements.txt
```

Run server:
```
sudo pigpio -n '127.0.0.1'
python3 main_server.py
```

##Client on pc:

Install python requirements:
```
pip3 install -r requirements.txt
```
Run client:
```
python3 main_client.py
```

