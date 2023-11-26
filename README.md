## Docker container monitoring with Zabbix

This is a Python script that collects data from Docker containers running on a host and then sends it over to a Zabbix server using the ZabbixSender/ZabbixTrapper functionality. 

As of now it collects 3 metrics: 

- Container status (running, exited, etc)
- Container exit code
- Container uptime

Triggers in the template are defined as so: 

- If the container has a non-zero exit code
- If the container uptime is less than 90 seconds

I've included the template files as example. The important part is that the name of the host defined in the Zabbix server **MUST** match the name that the script is sending over to Zabbix. If the container name does not match the hostname in the server, no data will be shown.


### Usage

#### Client-side

- Clone this repository on the server.
- In `main.py` edit the `zabbix_server` address and the `interval` value. Default is every 60 seconds.
- Create a virtual environment:
```
python3 -m venv env

```
- Activate the virtual environment and install the requirements:
```
source env/bin/activate
```
```
pip install --index-url http://172.20.14.54:5000/index/ --trusted-host 172.20.14.54 -r requirements.txt
```

- Create a systemd service file under `/etc/systemd/system/container-stats.service` with the following configuration: 

```
[Unit]
Description=Monitor container uptimes
After=network.target

[Service]
Type=simple
ExecStart=/opt/docker-container-monitoring/env/bin/python3 /opt/docker-container-monitoring/main.py
Restart=always
User=root
WorkingDirectory=/opt/docker-container-monitoring
StandardOutput=file:/opt/docker-container-monitoring/log/main.log
StandardError=file:/opt/docker-container-monitoring/log/error.log

[Install]
WantedBy=multi-user.target

```
- Reload and start the service
```
systemctl daemon-reload
```
```
systemctl enable container-stats.service
```
```
systemctl start container-stats.service
```

- logs can be accessed from the `logs/` directory


#### Zabbix server

- On the Zabbix server a template has been created named `Core containers`. Apply this container to your host. Make sure name matches the container name. 
