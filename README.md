# web-spectra-explorer

For deployment skip below to [deployment](#deployment).

## Goal

Pull integrated spectra from endpoint and display spectrum, waterfall plot. Allow to select a playback speed start time. Then smoothly transition bandwidths/etc.

This should all be running as an app and available by hitting some URL in modern browsers.

## Getting started

Setup a venv and source it

```bash
$ python3 -m venv venv
$ source venv/bin/activate
```

update pip

```bash
(venv)$ pip install --upgrade pip
```

Install requirements using the included [requirements.txt](./requirements.txt) file

```bash
(venv)$ pip install -r requirements.txt
```

Build the simulation data

```bash
(venv)$ python dataGenerator.py
```

Run the app.

```bash
(venv)$ python app.py
```

## Deployment

1. Spin up CC cloud instance (Ubuntu 20.04) using the [quick start guide](https://docs.computecanada.ca/wiki/Cloud_Quick_Start).

2. SSH into the VM.

3. Update the VM with `sudo apt update` and `sudo apt upgrade`

4. Install apache2 and wsgi with `sudo apt install apache2 libapache2-mod-wsgi-py3` (which we'll use to serve both the application and the data)

5. Clone this repo into `/home/ubuntu/` then install the venv and build the simulation dataset as described [above](#getting-started). You may want to take a look in [dataService.py](./dataService.py) and see how large a dataset is going to be generated. The current default is ~40 GB.

6. Make a folder in the home directory to host the server then move the simulated data into it

   ```bash
    cd
    mkdir public_html
    mkdir public_html/data
    mkdir public_html/wsgi
    mv web-spectra-explorer/data.h5 public_html/data/
    ```

7. Edit `web-spectra-explorer/dashApp.py` and change the line

    ```python
    simDataFile = h5py.File('data.h5','r')
    ```

    to be

    ```python
   simDataFile = h5py.File('/home/ubuntu/public_html/data/data.h5','r')

    ```


8. Create a file `public_html/wsgi/dash.wsgi` that contains

   ```python
   #!/usr/bin/python3
   import sys
   sys.path.insert(0, "/home/ubuntu/web-spectra-explorer/venv/lib/python3.8/site-packages")
   sys.path.insert(0,"/home/ubuntu/web-spectra-explorer/")
   from dashApp import server as application
   ```

9. Create a file `/etc/apache2/sites-available/dash.conf` that contains

   ```bash
   WSGIDaemonProcess dashApp user=ubuntu group=ubuntu home=/home/ubuntu threads=5
   WSGIScriptAlias /live /home/ubuntu/public_html/wsgi/dash.wsgi

   WSGIProcessGroup dashApp
   WSGIApplicationGroup %{GLOBAL}
   ```

10. Edit the `DocumentRoot` line in `/etc/apache2/sites-available/000-default.conf` to read

   ```bash 
   DocumentRoot /home/ubuntu/public_html
   ```

11. Edit `/etc/apache2/apache2.conf`.
    - Change the line `<Directory /var/www/html/>` to `<Directory /home/ubuntu/public_html/>`.
    - Add `RedirectMatch ^/$ /live` to the bottom of the file.

12. Restart the apache server with `sudo systemctl reload apache2`.

## Refs

[1](https://community.plotly.com/t/heatmap-is-slow-for-large-data-arrays/21007/3) To do with image resampling when zooming in.

[2](https://stackoverflow.com/questions/63589249/plotly-dash-display-real-time-data-in-smooth-animation) Intro to client-side callbacks and the extendData method.

[3](https://community.plotly.com/t/heatmap-performance-layout-and-related-questions/26899) Seems like someone was having this exact problem with large images. Will need to look into shaders.
