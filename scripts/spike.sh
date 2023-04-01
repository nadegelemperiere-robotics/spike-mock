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

# Gather parts database
mkdir -p /home/fll/.config/pyldraw
cp $scriptpath/../conf/config.yml /home/fll/.config/pyldraw/config.yml

# Install required python packages
pip install --quiet --no-warn-script-location -r $scriptpath/../requirements-test.txt
pip install --quiet --no-warn-script-location $scriptpath/../

# Launch python scripts to setup terraform environment
python3 test/demo/project.py

deactivate