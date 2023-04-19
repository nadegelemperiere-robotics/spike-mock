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
${CPTC_JSON_CONF_FILE}           ${data}/cptc.json
${CPRT_JSON_CONF_FILE}           ${data}/cprt.json
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
    [Teardown]         Reinitialize Scenario      ${scenario}

14.2 Test Speaker Behavior On Read Only Time Controlled Scenario
    [Tags]  Speaker
    ${scenario}        Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario     ${scenario}
    ${speaker}         Create Object      Speaker
    Use Object Method  ${speaker}    set_volume    False    -1    50
    Play Scenario During Steps     1
    ${volume}          Use Object Method  ${speaker}    get_volume    True
    Should Be Equal As Numbers     ${volume}    50
    Stop Scenario      ${scenario}
    [Teardown]         Reinitialize Scenario      ${scenario}

14.3 Test Speaker Behavior On Read Only Real Time Scenario
    [Tags]  Speaker
    ${scenario}        Create Scenario    ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario     ${scenario}
    ${speaker}         Create Object      Speaker
    Use Object Method  ${speaker}    set_volume    False    -1    50
    Sleep              0.1
    ${volume}          Use Object Method  ${speaker}    get_volume    True
    Should Be Equal As Numbers     ${volume}     50
    Stop Scenario      ${scenario}
    [Teardown]         Reinitialize Scenario      ${scenario}

14.4 Test Speaker Behavior On Computed Time Controlled Scenario
    [Tags]  Speaker
    ${scenario}        Create Scenario    ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario     ${scenario}
    ${speaker}         Create Object      Speaker
    Use Object Method  ${speaker}    set_volume    False    -1    50
    Play Scenario During Steps     1
    ${volume}          Use Object Method  ${speaker}    get_volume    True
    Should Be Equal As Numbers     ${volume}    50
    Stop Scenario      ${scenario}
    [Teardown]         Reinitialize Scenario      ${scenario}

14.5 Test Speaker Behavior On Computed Real Time Scenario
    [Tags]  Speaker
    ${scenario}        Create Scenario    ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario     ${scenario}
    ${speaker}         Create Object      Speaker
    Use Object Method  ${speaker}    set_volume    False    -1    50
    Sleep              0.1
    ${volume}          Use Object Method  ${speaker}    get_volume    True
    Should Be Equal As Numbers     ${volume}     50
    Stop Scenario      ${scenario}
    [Teardown]         Reinitialize Scenario      ${scenario}

14.6 Test The Parallel Behaviour Of Beep Functions On Read Only Time Controlled Scenario
    [Tags]  Speaker
    ${scenario}         Create Scenario     ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario      ${scenario}
    ${speaker}          Create Object      Speaker
    ${thread}           Start Method In A Thread    ${speaker}    beep    60    2
    Play Scenario During Steps  1
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps  10
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps  15
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    Stop Scenario       ${scenario}
    [Teardown]          Reinitialize Scenario      ${scenario}

14.7 Test The Parallel Behaviour Of Beep Functions On Read Only Real Time Scenario
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
    [Teardown]          Reinitialize Scenario      ${scenario}

14.8 Test The Parallel Behaviour Of Beep Functions On Computed Time Controlled Scenario
    [Tags]  Speaker
    ${scenario}         Create Scenario     ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario      ${scenario}
    ${speaker}          Create Object      Speaker
    ${thread}           Start Method In A Thread    ${speaker}    beep    60    2
    Play Scenario During Steps  1
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps  50
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps  75
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    Stop Scenario       ${scenario}
    [Teardown]          Reinitialize Scenario      ${scenario}

14.9 Test The Parallel Behaviour Of Beep Functions On Computed Real Time Scenario
    [Tags]  Speaker
    ${scenario}         Create Scenario     ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
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
    [Teardown]          Reinitialize Scenario      ${scenario}