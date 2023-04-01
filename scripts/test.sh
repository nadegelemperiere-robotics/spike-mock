#!/bin/bash
# -------------------------------------------------------
# TECHNOGIX
# -------------------------------------------------------
# Copyright (c) [2022] Technogix SARL
# All rights reserved
# -------------------------------------------------------
# Module to deploy an aws subnet with all the secure
# components required
# Bash script to tests in a container
# -------------------------------------------------------
# Nadège LEMPERIERE, @13 january 2022
# Latest revision: 13 january 2022
# -------------------------------------------------------

# Retrieve absolute path to this script
script=$(readlink -f $0)
scriptpath=`dirname $script`

# Launch tests in docker container
docker run  -it --rm \
            --volume $scriptpath/../:/package:rw \
            --volume $scriptpath/../../ldraw-parts:/parts:ro \
            --workdir /package \
            nadegelemperiere/fll-test-docker:v2.2.2  \
            ./scripts/robot.sh $@