# EleNa-Elevation-Based-Navigation
Project: EleNa-Elevation-Based-Navigation
Overview: This repository is for a web app that offers elevation based navigation. 
The user will be able to select the route between two points with a friendly 
graphical user interface that has: minimal elevation change or maximal elevation 
change. Our app is focused on providing additional fitness functionality. 
The user will be able to pick cycles (distance set by user) starting at their 
desired location and they will be able to choose to either 
include or exclude an area of rapid elevation change on the route "heartbreak hills".

Disclaimer: Due to geography, we cannot guarantee that such a heartbreak hill will be available for all routes 
(and of course there may be no way to avoid such a hill if the area picked to cycle on is very hilly)

<b>Languages</b>: Python, JavaScript, HTML/CSS. 
Utilizes the osmnx to interface with openstreetmap.

<b>Team Members:</b> Bryce Bodley-Gomes, Bochen Xu, Julian Oks, Sam Harris, Alex Behr.


# Setup
```
conda env create -f environment.yml
conda activate ox
cd Server
python Server.py
```

If you'd like to download new graphs, besides what's already in the saved graphs, be sure that you have a google maps api key in `path_finding/google_maps_api_key.txt`.

# Documentation
You can find documentation at `docs/build/html/index.html`.