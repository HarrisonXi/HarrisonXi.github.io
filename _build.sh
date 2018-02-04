#!/bin/sh
python ./_tools/tabToSpace.py
python ./_tools/readme.py
python ./_tools/compressPng.py ./source
