#!/bin/bash

python3 -mvenv .
/bin/bash -c ". bin/activate && pip install -r requirements.txt && collectors/fl/state_parks.py"
