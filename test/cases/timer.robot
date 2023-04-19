# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test spike timer mock
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

*** Settings ***
Documentation   A test case to check timer functioning
Library         ../keywords/objects.py
Library         ../keywords/scenario.py
Library         Collections


*** Variables ***
${ROTC_JSON_CONF_FILE}           ${data}/rotc.json
${RORT_JSON_CONF_FILE}           ${data}/rort.json
${ROBOT_JSON_CONF_FILE}          ${data}/robot.json

*** Test Cases ***
16.1 Ensure Timer Is Created With The Required Constants
    [Tags]  Timer
    ${scenario}      Create Scenario  ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    time
    Start Scenario   ${scenario}
    ${timer}         Create Object    Timer
    @{members} =     Create List    now    reset
    Should Have Members    ${timer}    ${members}
    [Teardown]       Reinitialize Scenario    ${scenario}

16.2 Test Timer Behavior On Time Controlled Scenario
    [Tags]  Timer
    ${scenario}        Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    time
    Start Scenario     ${scenario}
    Play Scenario During Steps    10
    ${timer1}          Create Object    Timer
    Use Object Method  ${timer1}    reset    False
    Play Scenario During Steps    20
    ${delay}           Use Object Method  ${timer1}    now    True
    Should Be Equal As Numbers    ${delay}    2
    ${timer2}          Create Object    Timer
    Use Object Method  ${timer2}    reset    False
    Play Scenario During Steps    1
    ${delay}           Use Object Method  ${timer2}    now    True
    Should Be Equal As Numbers    ${delay}    0.1
    [Teardown]         Reinitialize Scenario      ${scenario}

16.3 Test Timer Behavior On Real Time Scenario
    [Tags]  Timer
    ${scenario}        Create Scenario    ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    time
    Start Scenario     ${scenario}
    ${timer1}          Create Object    Timer
    Use Object Method  ${timer1}    reset    False
    Sleep              2
    ${delay}           Use Object Method  ${timer1}    now    True
    Should Be Equal As Numbers With Precision  ${delay}    2    0.03
    ${timer2}          Create Object    Timer
    Use Object Method  ${timer2}    reset    False
    Sleep              0.1
    ${delay}           Use Object Method  ${timer2}    now    True
    Should Be Equal As Numbers With Precision  ${delay}    0.1    0.03
    [Teardown]         Reinitialize Scenario      ${scenario}

16.4 Test The Parallel Behaviour Of Wait Functions On Time Controlled Scenario
    [Tags]  Timer
    ${scenario}         Create Scenario     ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    time
    Start Scenario      ${scenario}
    Play Scenario During Steps    1
    ${thread}           Start Function In A Thread    wait_for_seconds    2
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps    10
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps    20
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    [Teardown]          Reinitialize Scenario       ${scenario}

16.5 Test The Parallel Behaviour Of Wait functions On Real Time Scenario
    [Tags]  Timer
    ${scenario}         Create Scenario     ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    time
    Start Scenario      ${scenario}
    ${thread}           Start Function In A Thread    wait_for_seconds    2
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               1
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               1.1
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    [Teardown]          Reinitialize Scenario       ${scenario}

