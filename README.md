# FourSquare-Dataset

First approach to FourSquare Dataset processing data to detect friends patterns

# Instructions

To install the virtual enviroment:

1. `python3 -m venv venv`
2. `source ./venv/bin/activate`
3. `pip3 install -e .`
4. Install all missing dependencies: `surprise, pandas, numpy, click, pyproj, matplotlib`

To run the main script execute: `./experiments_tfg.sh`

# To execute the visual application locally:

In the file: FourSquare-Dataset/templates/maps/salida2.html

Modify the line:

`<script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?libraries=visualization&sensor=true_or_false&key=XXX"></script>`

Typing in the section `key=XXX` the api_key provided by your account in https://cloud.google.com/maps-platform/. Removed due to privacy and to avoid spam petitions.
