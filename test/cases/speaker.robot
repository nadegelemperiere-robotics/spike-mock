# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test spike hub speaker mock
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

*** Settings ***
Documentation   A test case to check hub speaker mock functioning
Library         ../keywords/objects.py
Library         ../keywords/scenario.py
Library         Collections

*** Variables ***
${ROTC_JSON_CONF_FILE}           ${data}/rotc.json
${RORT_JSON_CONF_FILE}           ${data}/rort.json
${ROBOT_JSON_CONF_FILE}          ${data}/robot.json

*** Test Cases ***

14.1 Ensure Speaker Is Created With The Required Constants
    [Tags]  Speaker
    ${scenario}        Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario     ${scenario}
    ${speaker}         Create Object    Speaker
    @{members} =       Create List    beep    start_beep    stop    get_volume    set_volume
    Should Have Members    ${speaker}    ${members}
    Stop Scenario      ${scenario}
    [Teardown]         Reset Scenario      ${scenario}

14.2 Test Speaker Behavior On Time Controlled Scenario
    [Tags]  Speaker
    ${scenario}        Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario     ${scenario}
    ${speaker}         Create Object      Speaker
    Play Scenario During Steps     1
    Use Object Method  ${speaker}    set_volume    False    -1    50
    ${volume}          Use Object Method  ${speaker}    get_volume    True
    Should Be Equal As Numbers     ${volume}    50
    Stop Scenario      ${scenario}
    [Teardown]         Reset Scenario      ${scenario}

14.3 Test Speaker Behavior On Real Time Scenario
    [Tags]  Speaker
    ${scenario}        Create Scenario    ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario     ${scenario}
    ${speaker}         Create Object      Speaker
    Use Object Method  ${speaker}    set_volume    False    -1    50
    ${volume}          Use Object Method  ${speaker}    get_volume    True
    Should Be Equal As Numbers     ${volume}     50
    Stop Scenario      ${scenario}
    [Teardown]         Reset Scenario      ${scenario}

14.4 Test The Parallel Behaviour Of Beep Functions On Time Controlled Scenario
    [Tags]  Speaker
    ${scenario}         Create Scenario     ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario      ${scenario}
    ${speaker}          Create Object      Speaker
    Play Scenario During Steps  1
    ${thread}           Start Method In A Thread    ${speaker}    beep    60    2
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps  10
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps  15
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    Stop Scenario       ${scenario}
    [Teardown]          Reset Scenario      ${scenario}

14.5 Test The Parallel Behaviour Of Beep Functions On Real Time Scenario
    [Tags]  Speaker
    ${scenario}         Create Scenario     ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario      ${scenario}
    ${speaker}          Create Object      Speaker
    ${thread}           Start Method In A Thread    ${speaker}    beep    60    2
    Sleep               1
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               0.9
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               0.2
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    Stop Scenario       ${scenario}
    [Teardown]          Reset Scenario      ${scenario}