# web-spectra-explorer

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
(venv)$ python dataService.py
```

Run the app.

```bash
(venv)$ python app.py
```

## Refs

[1](https://community.plotly.com/t/heatmap-is-slow-for-large-data-arrays/21007/3) To do with image resampling when zooming in.

[2](https://stackoverflow.com/questions/63589249/plotly-dash-display-real-time-data-in-smooth-animation) Intro to client-side callbacks and the extendData method.

[3](https://community.plotly.com/t/heatmap-performance-layout-and-related-questions/26899) Seems like someone was having this exact problem with large images. Will need to look into shaders.
