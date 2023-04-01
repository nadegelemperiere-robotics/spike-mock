#!/bin/bash
# -----------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Script to launch robotframework tests on common python
# classes
# -------------------------------------------------------
# Nadège LEMPERIERE, @01 november 2022
# Latest revision: 01 november 2022
# -------------------------------------------------------

# Retrieve absolute path to this script
script=$(readlink -f $0)
scriptpath=`dirname $script`


# Create virtual environment
python3 -m venv /home/fll/mock
. /home/fll/mock/bin/activate

# Install required python packages
pip install --quiet --no-warn-script-location sphinx-material
pip install --quiet --no-warn-script-location sphinx_rtd_theme
pip install --quiet --no-warn-script-location $scriptpath/../

# Launch python scripts to setup terraform environment
sphinx-apidoc -o docs/ spike/
sphinx-build -b html docs/ docs/build/html

deactivate