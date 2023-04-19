# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test spike hub button mock
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

*** Settings ***
Documentation   A test case to check hub button mock functioning
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

1.1 Ensure Button Is Created With The Required Constants
    [Tags]    Button
    ${scenario}          Create Scenario  ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    button
    Start Scenario       ${scenario}
    ${button}            Create Object    Button    left
    @{members} =         Create List      wait_until_pressed    wait_until_released    was_pressed    is_pressed
    Should Have Members  ${button}        ${members}
    [Teardown]           Reinitialize Scenario   ${scenario}

1.2 Test Button Behavior On Read Only Time Controlled Scenario
    [Tags]    Button
    ${scenario}         Create Scenario   ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    button
    Start Scenario      ${scenario}
    ${button}           Create Object     Button    left
    @{steps} =          Create List       34    20       2        46
    @{is_pressed} =     Create List
    @{was_pressed} =    Create List
    FOR    ${step}    IN    @{steps}
        ${shall_continue}   Play Scenario During Steps  ${step}
        ${is_p}             Use Object Method  ${button}    is_pressed    True
        ${was_p}            Use Object Method  ${button}    was_pressed    True
        Append To List      ${is_pressed}    ${is_p}
        Append To List      ${was_pressed}    ${was_p}
    END
    Should Be True      ${is_pressed[0]}
    Should Be True      ${was_pressed[0]}
    Should Not Be True  ${is_pressed[1]}
    Should Be True      ${was_pressed[1]}
    Should Not Be True  ${is_pressed[2]}
    Should Not Be True  ${was_pressed[2]}
    Should Be True      ${is_pressed[3]}
    Should Be True      ${was_pressed[3]}
    [Teardown]          Reinitialize Scenario   ${scenario}

1.3 Test Button Behavior On Read Only Real Time Scenario
    [Tags]    Button
    ${scenario}             Create Scenario   ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    button
    ${button}               Create Object     Button    left
    @{steps} =              Create List    3.4   2        0.2      4.6
    @{is_pressed} =         Create List
    @{was_pressed} =        Create List
    ${shall_continue} =     Set Variable      True
    ${previous_time} =      Get Time Milliseconds
    Start Scenario      ${scenario}
    FOR    ${step}    IN    @{steps}
        ${current_time} =    Get Time Milliseconds
        ${delta_time} =      Evaluate    ${step} - ${current_time} + ${previous_time}
        Sleep       ${delta_time}
        ${previous_time} =   Get Time Milliseconds
        ${is_p}             Use Object Method  ${button}    is_pressed    True
        ${was_p}            Use Object Method  ${button}    was_pressed   True
        Append To List      ${is_pressed}     ${is_p}
        Append To List      ${was_pressed}    ${was_p}
    END
    Stop Scenario       ${scenario}
    Should Be True      ${is_pressed[0]}
    Should Be True      ${was_pressed[0]}
    Should Not Be True  ${is_pressed[1]}
    Should Be True      ${was_pressed[1]}
    Should Not Be True  ${is_pressed[2]}
    Should Not Be True  ${was_pressed[2]}
    Should Be True      ${is_pressed[3]}
    Should Be True      ${was_pressed[3]}
    [Teardown]     Reinitialize Scenario   ${scenario}

1.4 Test Button Behavior On Computed Time Controlled Scenario
    [Tags]    Button
    ${scenario}         Create Scenario   ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    button
    Start Scenario      ${scenario}
    ${button}           Create Object     Button    left
    Use Object Method   ${scenario}       push_button    False    -1    left
    ${shall_continue}   Play Scenario During Steps    1
    ${is_p}             Use Object Method  ${button}    is_pressed    True
    ${was_p}            Use Object Method  ${button}    was_pressed    True
    Should Be True      ${is_p}
    Should Be True      ${was_p}
    ${shall_continue}   Play Scenario During Steps    10
    ${is_p}             Use Object Method  ${button}    is_pressed    True
    ${was_p}            Use Object Method  ${button}    was_pressed    True
    Should Be True      ${is_p}
    Should Be True      ${was_p}
    Use Object Method   ${scenario}       release_button    False    -1    left
    ${shall_continue}   Play Scenario During Steps    1
    ${is_p}             Use Object Method  ${button}    is_pressed    True
    ${was_p}            Use Object Method  ${button}    was_pressed    True
    Should Not Be True  ${is_p}
    Should Not Be True  ${was_p}
    Use Object Method   ${scenario}       push_button    False    -1    left
    ${shall_continue}   Play Scenario During Steps    1
    Use Object Method   ${scenario}       release_button    False    -1    left
    ${shall_continue}   Play Scenario During Steps    1
    ${is_p}             Use Object Method  ${button}    is_pressed    True
    ${was_p}            Use Object Method  ${button}    was_pressed    True
    Should Not Be True  ${is_p}
    Should Be True      ${was_p}
    [Teardown]          Reinitialize Scenario   ${scenario}

1.5 Test Button Behavior On Computed Real Time Scenario
    [Tags]    Button
    ${scenario}         Create Scenario   ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    button
    Start Scenario      ${scenario}
    ${button}           Create Object     Button    left
    Use Object Method   ${scenario}       push_button    False    -1    left
    Sleep               0.1
    ${is_p}             Use Object Method  ${button}    is_pressed    True
    ${was_p}            Use Object Method  ${button}    was_pressed    True
    Should Be True      ${is_p}
    Should Be True      ${was_p}
    Sleep               2
    ${is_p}             Use Object Method  ${button}    is_pressed    True
    ${was_p}            Use Object Method  ${button}    was_pressed    True
    Should Be True      ${is_p}
    Should Be True      ${was_p}
    Use Object Method   ${scenario}       release_button    False    -1    left
    Sleep               0.1
    ${is_p}             Use Object Method  ${button}    is_pressed    True
    ${was_p}            Use Object Method  ${button}    was_pressed    True
    Should Not Be True  ${is_p}
    Should Not Be True  ${was_p}
    Use Object Method   ${scenario}       push_button    False    -1    left
    Sleep               0.1
    Use Object Method   ${scenario}       release_button    False    -1    left
    Sleep               0.1
    ${is_p}             Use Object Method  ${button}    is_pressed    True
    ${was_p}            Use Object Method  ${button}    was_pressed    True
    Should Not Be True  ${is_p}
    Should Be True      ${was_p}
    [Teardown]          Reinitialize Scenario   ${scenario}

1.6 Test The Parallel Behaviour Of Wait Functions On Read Only Time Controlled Scenario
    [Tags]              Button
    ${scenario}         Create Scenario      ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    button
    Start Scenario      ${scenario}
    ${button}           Create Object        Button    left
    ${thread}           Start Method In A Thread    ${button}    wait_until_pressed
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    ${shall_continue}   Play Scenario During Steps    36
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${button}    wait_until_released
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    ${shall_continue}   Play Scenario During Steps    20
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    [Teardown]          Reinitialize Scenario       ${scenario}

1.7 Test The Parallel Behaviour Of Wait Functions On Read Only Real Time Scenario
    [Tags]              Button
    ${scenario}         Create Scenario      ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    button
    Start Scenario      ${scenario}
    ${button}           Create Object        Button    left
    ${thread}           Start Method In A Thread    ${button}    wait_until_pressed
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               3.6
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${button}    wait_until_released
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               2
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    [Teardown]          Reinitialize Scenario       ${scenario}

1.8 Test The Parallel Behaviour Of Wait Functions On Computed Time Controlled Scenario
    [Tags]              Button
    ${scenario}         Create Scenario      ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    button
    Start Scenario      ${scenario}
    ${button}           Create Object        Button    left
    ${thread}           Start Method In A Thread    ${button}    wait_until_pressed
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    ${shall_continue}   Play Scenario During Steps    36
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Use Object Method   ${scenario}       push_button    False    -1    left
    ${shall_continue}   Play Scenario During Steps    1
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${button}    wait_until_released
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    ${shall_continue}   Play Scenario During Steps    20
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Use Object Method   ${scenario}       release_button    False    -1    left
    ${shall_continue}   Play Scenario During Steps    1
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    [Teardown]          Reinitialize Scenario       ${scenario}

1.9 Test The Parallel Behaviour Of Wait Functions On Computed Real Time Scenario
    [Tags]              Button
    ${scenario}         Create Scenario      ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    button
    Start Scenario      ${scenario}
    ${button}           Create Object        Button    left
    ${thread}           Start Method In A Thread    ${button}    wait_until_pressed
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               2
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Use Object Method   ${scenario}       push_button    False    -1    left
    Sleep               0.1
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${thread}           Start Method In A Thread    ${button}    wait_until_released
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               2
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Use Object Method   ${scenario}       release_button    False    -1    left
    Sleep               0.1
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    [Teardown]          Reinitialize Scenario       ${scenario}