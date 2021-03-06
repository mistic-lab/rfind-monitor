# RFInd Monitor

For deployment skip below to [deployment](#deployment).

## Suggested installation steps

Setup a venv and source it

```bash
python3 -m venv venv
source venv/bin/activate
```

update pip

```bash
(venv)$ pip install --upgrade pip
```

Install this package and it's requirements with

```bash
(venv)$ pip install .
```

> Add a `-e` flag to make it editable if you're changing the code or regularly updating the repo

### Install Redis

```bash
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
make test
sudo make install
```

### Test the app with simulated data

Build the simulation data

```bash
(venv)$ python -m rfind_monitor.sim.data_gen
```

> To use the local zmq simulation, move the new `data.h5` file into `/rfind_monitor/sim/`.

Run the app.

```bash
(venv)$ python -m rfind_monitor.frontend.dash
```

In a separate terminal (sourcing the same venv) run the Redis server

```
(venv)$ python -m rfind_monitor.backend.redis_store
```

In a separate terminal (sourcing the same venv) run the middle man.

```bash
(venv)$ python -m rfind_monitor.backend.middle_man
```

In a separate terminal (sourcing the same venv) run the data server

```bash
(venv)$ python -m rfind_monitor.sim.zmq_pusher
```

The middle man handles the zmq binding that has data pushed to it and writes that to the Redis storage.

## Deployment

1. Spin up CC cloud instance (Ubuntu 20.04) using the [quick start guide](https://docs.computecanada.ca/wiki/Cloud_Quick_Start).

2. SSH into the VM.

3. Update the VM with `sudo apt update` and `sudo apt upgrade`

4. Install some dependencies with `sudo apt install apache2 libapache2-mod-wsgi-py3 python3-venv` (which we'll use to serve both the application and the data)

5. Clone this repo into `/home/ubuntu/` then install the venv and this package as described [above](#suggested-installation-steps). Make sure to install redis as well as decribed above.

6. Make a folder in the home directory to host the server

   ```bash
    cd
    mkdir public_html
    mkdir public_html/data
    mkdir public_html/wsgi
    ```

7. Create a file `public_html/wsgi/dash.wsgi` that contains

   ```python
   #!/usr/bin/python3
   import sys
   sys.path.insert(0, "/home/ubuntu/rfind-monitor/venv/lib/python3.8/site-packages")
   from rfind_monitor.frontend.dash import server as application
   ```

8. Create a file `/etc/apache2/sites-available/dash.conf` that contains

   ```bash
   WSGIDaemonProcess dash user=ubuntu group=ubuntu home=/home/ubuntu threads=5 socket-user=#33
   WSGIScriptAlias /live /home/ubuntu/public_html/wsgi/dash.wsgi

   WSGIProcessGroup dash
   WSGIApplicationGroup %{GLOBAL}
   ```

9. Edit `/etc/apache2/sites-available/000-default.conf`:
    - Change the line `DocumentRoot /var/www` to `DocumentRoot /home/ubuntu/public_html`

10. Edit `/etc/apache2/apache2.conf`
    - Change the line `<Directory /var/www/>` to `<Directory /home/ubuntu/public_html/>`.
    - Add `RedirectMatch ^/$ /live` to the bottom of the file.

11. Enable the new wsgi site using `sudo /usr/sbin/a2ensite dash.conf`

12. Restart the apache server with `sudo systemctl reload apache2`.

13. Move the redis service file into its location and start the service.

    ```bash
    sudo cp /home/ubuntu/rfind-monitor/conf/redis.service /etc/systemd/system/redis.service
    sudo systemctl enable /etc/systemd/system/redis.service
    sudo systemctl start redis.service
    ```

    There are also a few lines you need to add to the `redis.conf` file - ask Nick for details.

14. Move the middle man service file into its location and start the service.

    ```bash
    sudo cp /home/ubuntu/rfind-monitor/conf/middleman.service /etc/systemd/system/middleman.service
    sudo systemctl enable /etc/systemd/system/middleman.service
    sudo systemctl start middleman.service
    ```

## Refs

### DASH

[1](https://stackoverflow.com/questions/63589249/plotly-dash-display-real-time-data-in-smooth-animation) Intro to client-side callbacks and the extendData method.

[2](https://community.plotly.com/t/heatmap-performance-layout-and-related-questions/26899) Seems like someone was having this exact problem with large images. Will need to look into shaders.

### DEPLOYMENT

[3](https://community.plotly.com/t/deploy-dash-on-apache-server-solved/4855/14) Not much in here honestly. The user was on the wrong py version.

[4](https://stackoverflow.com/questions/62481788/dash-deployed-on-apache-server-failing-with-dash-object-not-callable) Explains wsgi conf file.

[5](https://stackoverflow.com/questions/62994338/deploying-dash-app-on-apache-using-mod-wsgi) An example.

[6](https://stackoverflow.com/questions/66218282/how-do-i-host-a-dash-app-on-an-apache-server) I always forgot this. Don't forget to `a2ensuite`!
