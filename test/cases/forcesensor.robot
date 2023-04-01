# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test spike force sensor mock
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

*** Settings ***
Documentation   A test case to check force sensor mock functioning
Library         ../keywords/objects.py
Library         ../keywords/scenario.py
Library         Collections

*** Variables ***
${ROTC_JSON_CONF_FILE}           ${data}/rotc.json
${RORT_JSON_CONF_FILE}           ${data}/rort.json
${ROBOT_JSON_CONF_FILE}          ${data}/robot.json

*** Test Cases ***

6.1 Ensure Force Sensor Is Created With The Required Constants
    [Tags]    ForceSensor
    ${scenario}      Create Scenario  ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    force
    Start Scenario   ${scenario}
    ${sensor}        Create Object  ForceSensor    B
    @{members} =     Create List    wait_until_pressed    wait_until_released    is_pressed    get_force_newton    get_force_percentage
    Should Have Members    ${sensor}    ${members}
    [Teardown]     Reset Scenario   ${scenario}

6.2 Test Force Sensor Behavior On Read Only Time Controlled Scenario
    [Tags]    ForceSensor
    ${scenario}             Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    force
    Start Scenario          ${scenario}
    ${sensor}               Create Object      ForceSensor    B
    @{steps} =              Create List    19    9      11    10    20
    @{is_pressed} =         Create List
    @{force} =              Create List    0     1.2    7     9.2    0
    @{force_percentage} =   Create List    0     12     70    92     0
    ${i_step} =         Set Variable    0
    ${i_step} =         Convert To Integer  ${i_step}
    FOR    ${step}    IN    @{steps}
        Play Scenario During Steps     ${step}
        ${is_p}         Use Object Method  ${sensor}    is_pressed    True
        ${f}        Use Object Method  ${sensor}    get_force_newton        True    -1
        ${p}        Use Object Method  ${sensor}    get_force_percentage    True    -1
        Append To List  ${is_pressed}    ${is_p}
        ${ft}       Get From List      ${force}              ${i_step}
        ${pt}       Get From List      ${force_percentage}   ${i_step}
        Should Be Equal As Numbers     ${ft}     ${f}
        Should Be Equal As Integers    ${pt}     ${p}
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    Should Not Be True  ${is_pressed[0]}
    Should Not Be True  ${is_pressed[1]}
    Should Be True      ${is_pressed[2]}
    Should Be True      ${is_pressed[3]}
    Should Not Be True  ${is_pressed[4]}
    [Teardown]     Reset Scenario   ${scenario}

6.3 Test Force Sensor Behavior On Read Only Real Time Scenario
    [Tags]    ForceSensor
    ${scenario}             Create scenario    ${RORT_JSON_CONF_FILE}     ${ROBOT_JSON_CONF_FILE}    force
    @{steps} =              Create List    1.9   0.9    1.1   1      2
    @{is_pressed} =         Create List
    @{force} =              Create List    0     1.2    7     9.2    0
    @{force_percentage} =   Create List    0     12     70    92     0
    ${i_step} =             Set Variable    0
    ${i_step} =             Convert To Integer  ${i_step}
    ${previous_time} =      Get Time Milliseconds
    Start Scenario          ${scenario}
    ${sensor}               Create Object      ForceSensor    B
    FOR    ${step}    IN    @{steps}
        ${current_time} =    Get Time Milliseconds
        ${delta_time} =      Evaluate    ${step} - ${current_time} + ${previous_time}
        Sleep       ${delta_time}
        ${previous_time} =   Get Time Milliseconds
        ${is_p}         Use Object Method  ${sensor}    is_pressed    True
        ${f}        Use Object Method  ${sensor}    get_force_newton        True    -1
        ${p}        Use Object Method  ${sensor}    get_force_percentage    True    -1
        Append To List  ${is_pressed}    ${is_p}
        ${ft}       Get From List      ${force}              ${i_step}
        ${pt}       Get From List      ${force_percentage}   ${i_step}
        Should Be Equal As Numbers With Precision    ${ft}     ${f}    0.1
        Should Be Equal As Numbers With Precision    ${pt}     ${p}    5
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    Should Not Be True  ${is_pressed[0]}
    Should Not Be True  ${is_pressed[1]}
    Should Be True      ${is_pressed[2]}
    Should Be True      ${is_pressed[3]}
    Should Not Be True  ${is_pressed[4]}
    [Teardown]     Reset Scenario   ${scenario}

6.4 Test The Parallel Behaviour Of Wait Functions On Time Controlled Scenario
    [Tags]    ForceSensor
    ${scenario}         Create scenario    ${ROTC_JSON_CONF_FILE}        ${ROBOT_JSON_CONF_FILE}  force
    Start Scenario      ${scenario}
    ${sensor}           Create Object      ForceSensor    B
    ${thread}           Start Method In A Thread    ${sensor}    wait_until_pressed
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps    35
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${sensor}    wait_until_released
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps    25
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    [Teardown]          Reset Scenario   ${scenario}

6.5 Test The Parallel Behaviour Of Wait Functions On Real Time Scenario
    [Tags]    ForceSensor
    ${scenario}         Create Scenario    ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  force
    Start Scenario      ${scenario}
    ${sensor}           Create Object      ForceSensor    B
    ${thread}           Start Method In A Thread    ${sensor}    wait_until_pressed
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               3.5
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${sensor}    wait_until_released
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               2.5
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    [Teardown]          Reset Scenario   ${scenario}
