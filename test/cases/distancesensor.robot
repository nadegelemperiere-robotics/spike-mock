# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test spike distance sensor mock
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

*** Settings ***
Documentation   A test case to check distance sensor mock functioning
Library         ../keywords/objects.py
Library         ../keywords/scenario.py
Library         Collections

*** Variables ***
${ROTC_JSON_CONF_FILE}           ${data}/rotc.json
${RORT_JSON_CONF_FILE}           ${data}/rort.json
${ROBOT_JSON_CONF_FILE}          ${data}/robot.json

*** Test Cases ***

4.1 Ensure Distance Sensor Is Created With The Required Constants
    [Tags]    DistanceSensor
    ${scenario}      Create Scenario         ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  distance
    ${sensor}        Create Object    DistanceSensor    C
    Start Scenario   ${scenario}
    @{members} =     Create List    get_distance_cm    get_distance_inches    get_distance_percentage    wait_for_distance_farther_than    wait_for_distance_closer_than     light_up     light_up_all
    Should Have Members    ${sensor}    ${members}
    [Teardown]       Reinitialize Scenario   ${scenario}

4.2 Ensure Error Management Is Correctly Implemented
    [Tags]    DistanceSensor
    ${scenario}         Create Scenario         ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  distance
    ${sensor}           Create Object    DistanceSensor    C
    Start Scenario      ${scenario}
    Run Keyword And Expect Error    TypeError: brightness is not an integer     Use Object Method  ${sensor}     light_up_all    False    -1    12.5
    Run Keyword And Expect Error    TypeError: right_top is not an integer      Use Object Method  ${sensor}     light_up        False    -1    12.5  50    50    50
    Run Keyword And Expect Error    TypeError: left_top is not an integer       Use Object Method  ${sensor}     light_up        False    -1    50    12.5  50    50
    Run Keyword And Expect Error    TypeError: right_bottom is not an integer   Use Object Method  ${sensor}     light_up        False    -1    50    50    12.5  50
    Run Keyword And Expect Error    TypeError: left_bottom is not an integer    Use Object Method  ${sensor}     light_up        False    -1    50    50    50    12.5
    [Teardown]     Reinitialize Scenario   ${scenario}

4.3 Test Distance Sensor Behavior On Read Only Time Controlled Scenario
    [Tags]    DistanceSensor
    ${scenario}         Create Scenario         ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  distance
    Start Scenario                 ${scenario}
    ${sensor}                      Create Object    DistanceSensor    C
    @{steps} =                     Create List    3      20     10     15     25
    @{distance_cm_lr} =            Create List    -1     70     40     160    -1
    @{distance_inches_lr} =        Create List    -1     28     16     63     -1
    @{distance_percentage_lr} =    Create List    -1     35     20     80     -1
    @{distance_cm_sr} =            Create List    -1     -1     40     -1     -1
    @{distance_inches_sr} =        Create List    -1     -1     16     -1     -1
    @{distance_percentage_sr} =    Create List    -1     -1     20     -1     -1
    ${i_step} =         Set Variable    0
    ${i_step} =         Convert To Integer  ${i_step}
    FOR    ${step}    IN    @{steps}
        Play Scenario During Steps     ${step}
        ${c}        Use Object Method  ${sensor}    get_distance_cm            True    -1
        ${i}        Use Object Method  ${sensor}    get_distance_inches        True    -1
        ${p}        Use Object Method  ${sensor}    get_distance_percentage    True    -1
        ${ct}       Get From List      ${distance_cm_lr}           ${i_step}
        ${it}       Get From List      ${distance_inches_lr}       ${i_step}
        ${pt}       Get From List      ${distance_percentage_lr}   ${i_step}
        Should Be Equal As Integers    ${ct}     ${c}
        Should Be Equal As Integers    ${it}     ${i}
        Should Be Equal As Integers    ${pt}     ${p}
        ${c}        Use Object Method  ${sensor}    get_distance_cm            True    -1    True
        ${i}        Use Object Method  ${sensor}    get_distance_inches        True    -1    True
        ${p}        Use Object Method  ${sensor}    get_distance_percentage    True    -1    True
        ${ct}       Get From List      ${distance_cm_sr}           ${i_step}
        ${it}       Get From List      ${distance_inches_sr}       ${i_step}
        ${pt}       Get From List      ${distance_percentage_sr}   ${i_step}
        Should Be Equal As Integers    ${ct}     ${c}
        Should Be Equal As Integers    ${it}     ${i}
        Should Be Equal As Integers    ${pt}     ${p}
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]       Reinitialize Scenario   ${scenario}

4.4 Test Distance Sensor Behavior On Read Only Real Time Scenario
    [Tags]    DistanceSensor
    ${scenario}         Create Scenario         ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  distance
    ${sensor}                      Create Object      DistanceSensor    C
    @{steps} =                     Create List    0.3    2      1      1.5    2.5
    @{distance_cm_lr} =            Create List    -1     70     40     160    -1
    @{distance_inches_lr} =        Create List    -1     28     16     63     -1
    @{distance_percentage_lr} =    Create List    -1     35     20     80     -1
    @{distance_cm_sr} =            Create List    -1     -1     40     -1     -1
    @{distance_inches_sr} =        Create List    -1     -1     16     -1     -1
    @{distance_percentage_sr} =    Create List    -1     -1     20     -1     -1
    ${i_step} =                    Set Variable    0
    ${i_step} =                    Convert To Integer  ${i_step}
    ${previous_time} =             Get Time Milliseconds
    Start Scenario      ${scenario}
    FOR    ${step}    IN    @{steps}
        ${current_time} =    Get Time Milliseconds
        ${delta_time} =      Evaluate    ${step} - ${current_time} + ${previous_time}
        Sleep       ${delta_time}
        ${previous_time} =   Get Time Milliseconds
        ${c}        Use Object Method  ${sensor}    get_distance_cm            True    -1
        ${i}        Use Object Method  ${sensor}    get_distance_inches        True    -1
        ${p}        Use Object Method  ${sensor}    get_distance_percentage    True    -1
        ${ct}       Get From List      ${distance_cm_lr}           ${i_step}
        ${it}       Get From List      ${distance_inches_lr}       ${i_step}
        ${pt}       Get From List      ${distance_percentage_lr}   ${i_step}
        Should Be Equal As Numbers With Precision      ${ct}     ${c}    7
        Should Be Equal As Numbers With Precision      ${it}     ${i}    3
        Should Be Equal As Numbers With Precision      ${pt}     ${p}    3
        ${c}        Use Object Method  ${sensor}    get_distance_cm            True    -1    True
        ${i}        Use Object Method  ${sensor}    get_distance_inches        True    -1    True
        ${p}        Use Object Method  ${sensor}    get_distance_percentage    True    -1    True
        ${ct}       Get From List      ${distance_cm_sr}           ${i_step}
        ${it}       Get From List      ${distance_inches_sr}       ${i_step}
        ${pt}       Get From List      ${distance_percentage_sr}   ${i_step}
        Should Be Equal As Numbers With Precision      ${ct}     ${c}    7
        Should Be Equal As Numbers With Precision      ${it}     ${i}    3
        Should Be Equal As Numbers With Precision      ${pt}     ${p}    3
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]       Reinitialize Scenario   ${scenario}

4.5 Test The Parallel Behaviour Of Wait Functions On Time Controlled Scenario
    [Tags]  DistanceSensor
    ${scenario}         Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  distance
    Start Scenario      ${scenario}
    ${sensor}           Create Object      DistanceSensor    C
    Play Scenario During Steps    9
    ${thread}           Start Method In A Thread    ${sensor}    wait_for_distance_closer_than    170    cm    False
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps    20
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${sensor}    wait_for_distance_farther_than    160    cm    False
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps    60
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${sensor}    wait_for_distance_closer_than     30    cm    True
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps    50
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${sensor}    wait_for_distance_farther_than    40    cm    True
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps    45
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    [Teardown]          Reinitialize Scenario   ${scenario}

4.6 Test The Parallel Behaviour Of Wait Functions On Real Time Scenario
    [Tags]  DistanceSensor
    ${scenario}         Create Scenario    ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  distance
    ${sensor}           Create Object      DistanceSensor    C
    Start Scenario      ${scenario}
    Sleep               0.9
    ${thread}           Start Method In A Thread    ${sensor}    wait_for_distance_closer_than    170    cm    False
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               2
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${sensor}    wait_for_distance_farther_than    160    cm    False
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               6
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${sensor}    wait_for_distance_closer_than     30    cm    True
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               5
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${sensor}    wait_for_distance_farther_than    40    cm    True
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               4.5
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    [Teardown]          Reinitialize Scenario   ${scenario}

