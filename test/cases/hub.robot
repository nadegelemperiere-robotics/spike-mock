# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test spike hub mock
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

*** Settings ***
Documentation   A test case to check hub mock functioning
Library         ../keywords/objects.py
Library         ../keywords/scenario.py

*** Variables ***
${ROTC_JSON_CONF_FILE}           ${data}/rotc.json
${ROBOT_JSON_CONF_FILE}          ${data}/robot.json

*** Test Cases ***

7.1 Ensure Hub Is Created With The Required Constants
    [Tags]    Hub
    ${scenario}     Create Scenario     ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    ${hub}          Create Object    Hub
    @{members} =    Create List    left_button    right_button    speaker    light_matrix    status_light    motion_sensor
    Should Have Members    ${hub}    ${members}
    [Teardown]      Reset Scenario   ${scenario}