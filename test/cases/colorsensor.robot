# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test spike color sensor mock
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

*** Settings ***
Documentation   A test case to check color sensor mock functioning
Library         ../keywords/objects.py
Library         ../keywords/scenario.py
Library         ../keywords/dynamics.py
Library         Collections

*** Variables ***
${ROTC_JSON_CONF_FILE}           ${data}/rotc.json
${RORT_JSON_CONF_FILE}           ${data}/rort.json
${CPTC_JSON_CONF_FILE}           ${data}/cptc.json
${CPRT_JSON_CONF_FILE}           ${data}/cprt.json
${TEST_FILE}                     ${data}/dynamics.xlsm
${ROBOT_JSON_CONF_FILE}          ${data}/robot.json

*** Test Cases ***

2.1 Ensure Color Sensor Is Created With The Required Constants
    [Tags]    ColorSensor
    ${scenario}      Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    color
    ${sensor}        Create Object      ColorSensor    A
    Start Scenario   ${scenario}
    @{members} =     Create List      get_color    get_ambiant_light    get_reflected_light    get_rgb_intensity    get_red     get_green     get_blue     wait_until_color    wait_for_new_color     light_up     light_up_all
    Should Have Members    ${sensor}    ${members}
    [Teardown]       Reinitialize Scenario   ${scenario}

2.2 Ensure Error Management Is Correctly Implemented
    [Tags]  ColorSensor
    ${scenario}      Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    color
    ${sensor}        Create Object      ColorSensor    A
    Start Scenario   ${scenario}
    Run Keyword And Expect Error    TypeError: brightness is not an integer    Use Object Method  ${sensor}     light_up_all    False    -1    12.5
    Run Keyword And Expect Error    TypeError: light_1 is not an integer       Use Object Method  ${sensor}     light_up        False    -1    12.5  50    50
    Run Keyword And Expect Error    TypeError: light_2 is not an integer       Use Object Method  ${sensor}     light_up        False    -1    50    12.5    50
    Run Keyword And Expect Error    TypeError: light_3 is not an integer       Use Object Method  ${sensor}     light_up        False    -1    50    50    12.5
    [Teardown]       Reinitialize Scenario   ${scenario}

2.3 Test Color Sensor Behavior On Read Only Time Controlled Scenario
    [Tags]  ColorSensor
    ${scenario}         Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    color
    Start Scenario      ${scenario}
    ${sensor}           Create Object      ColorSensor    A
    @{steps} =          Create List    39      20       30      50       50
    @{red} =            Create List    1024    0        1024    0        0
    @{blue} =           Create List    1024    0        0       0        1024
    @{green} =          Create List    1024    0        0       1024     0
    @{color} =          Create List    white   black    red     green    blue
    @{ambiant} =        Create List    0       0        0       0        0
    @{reflected} =      Create List    100     100      100     100      100
    ${i_step} =         Set Variable    0
    ${i_step} =         Convert To Integer  ${i_step}
    FOR    ${step}    IN    @{steps}
        Play Scenario During Steps     ${step}
        ${r}        Use Object Method  ${sensor}    get_red                True
        ${g}        Use Object Method  ${sensor}    get_green              True
        ${b}        Use Object Method  ${sensor}    get_blue               True
        ${c}        Use Object Method  ${sensor}    get_color              True
        ${a}        Use Object Method  ${sensor}    get_ambiant_light      True
        ${rf}       Use Object Method  ${sensor}    get_reflected_light    True
        ${i}        Use Object Method  ${sensor}    get_rgb_intensity      True
        ${rt}       Get From List      ${red}          ${i_step}
        ${gt}       Get From List      ${green}        ${i_step}
        ${bt}       Get From List      ${blue}         ${i_step}
        ${ct}       Get From List      ${color}        ${i_step}
        ${at}       Get From List      ${ambiant}      ${i_step}
        ${rft}      Get From List      ${reflected}    ${i_step}
        Should Be Equal As Integers    ${rt}     ${r}
        Should Be Equal As Integers    ${gt}     ${g}
        Should Be Equal As Integers    ${bt}     ${b}
        Should Be Equal                ${ct}     ${c}
        Should Be Equal As Integers    ${at}     ${a}
        Should Be Equal As Integers    ${rft}    ${rf}
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]       Reinitialize Scenario   ${scenario}

2.4 Test Color Sensor Behavior On Computed Time Controlled Scenario
    [Tags]  ColorSensor
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    color
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    color
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${sensor}       Create Object    ColorSensor  A
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]     ${i_step}
        ${east}        Get From List      ${tests}[east]      ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]       ${i_step}
        ${left}        Get From List      ${tests}[left]      ${i_step}
        ${right}       Get From List      ${tests}[right]     ${i_step}
        ${steering}    Get From List      ${tests}[steering]  ${i_step}
        ${speed}       Get From List      ${tests}[speed]     ${i_step}
        ${steps}       Evaluate    ${duration} / 0.02 + 1
        Start Scenario  ${scenario}
        # Turn 45°
        ${thread}           Start Method In A Thread    ${motor}    move    3.118030704    cm    100    50
        Play Scenario During Steps  10
        Sleep               1
        ${is_alive}         Is Thread Running    ${thread}
        Should Not Be True  ${is_alive}
        ${status}           Use Object Method  ${scenario}    status       True
        # Move to reach (60,60)
        ${thread}           Start Method In A Thread    ${motor}    move     84.85281374    cm    0      50
        Play Scenario During Steps  250
        Sleep               1
        ${is_alive}         Is Thread Running    ${thread}
        Should Not Be True  ${is_alive}
        ${status}           Use Object Method  ${scenario}    status       True
        # Reorient
        ${thread}           Start Method In A Thread    ${motor}    move     3.118030704    cm    -100   50
        Play Scenario During Steps  10
        Sleep               1
        ${is_alive}         Is Thread Running    ${thread}
        Should Not Be True  ${is_alive}
        ${status}           Use Object Method  ${scenario}    status       True
        # Start
        Use Object Method    ${motor}    start    False    -1    ${steering}    ${speed}
        Play Scenario During Steps  ${steps}
        Sleep                       1
        Use Object Method    ${motor}    stop
        ${status}       Use Object Method  ${scenario}    status       True
        ${color}        Use Object Method  ${sensor}      get_color    True    None
        ${red}          Use Object Method  ${sensor}      get_red      True
        ${blue}         Use Object Method  ${sensor}      get_blue     True
        ${green}        Use Object Method  ${sensor}      get_green    True
        ${rt}       Get From List      ${tests}[red]      ${i_step}
        ${gt}       Get From List      ${tests}[green]    ${i_step}
        ${bt}       Get From List      ${tests}[blue]     ${i_step}
        ${ct}       Get From List      ${tests}[color]    ${i_step}
        Should Be Equal As Numbers With Precision     ${green}    ${gt}       1
        Should Be Equal As Numbers With Precision     ${blue}     ${bt}       1
        Should Be Equal As Numbers With Precision     ${red}      ${rt}       1
        Should Be Equal                               ${color}    ${ct}
        Stop Scenario  ${scenario}
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reinitialize Scenario  ${scenario}

2.5 Test Color Sensor Behavior On Read Only Real Time Scenario
    [Tags]  ColorSensor
    ${scenario}         Create Scenario    ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    color
    ${sensor}           Create Object      ColorSensor    A
    @{steps} =          Create List    3.9     2        3       5        5
    @{red} =            Create List    1024    0        1024    0        0
    @{blue} =           Create List    1024    0        0       0        1024
    @{green} =          Create List    1024    0        0       1024     0
    @{color} =          Create List    white   black    red     green    blue
    @{ambiant} =        Create List    0       0        0       0        0
    @{reflected} =      Create List    100     100      100     100      100
    ${i_step} =         Set Variable    0
    ${i_step} =         Convert To Integer  ${i_step}
    ${previous_time} =  Get Time Milliseconds
    Start Scenario      ${scenario}
    FOR    ${step}    IN    @{steps}
        ${current_time} =    Get Time Milliseconds
        ${delta_time} =      Evaluate    ${step} - ${current_time} + ${previous_time}
        Sleep       ${delta_time}
        ${previous_time} =   Get Time Milliseconds
        ${r}        Use Object Method  ${sensor}    get_red                True
        ${g}        Use Object Method  ${sensor}    get_green              True
        ${b}        Use Object Method  ${sensor}    get_blue               True
        ${c}        Use Object Method  ${sensor}    get_color              True
        ${a}        Use Object Method  ${sensor}    get_ambiant_light      True
        ${rf}       Use Object Method  ${sensor}    get_reflected_light    True
        ${i}        Use Object Method  ${sensor}    get_rgb_intensity      True
        ${rt}       Get From List      ${red}          ${i_step}
        ${gt}       Get From List      ${green}        ${i_step}
        ${bt}       Get From List      ${blue}         ${i_step}
        ${ct}       Get From List      ${color}        ${i_step}
        ${at}       Get From List      ${ambiant}      ${i_step}
        ${rft}      Get From List      ${reflected}    ${i_step}
        Should Be Equal As Integers    ${rt}     ${r}
        Should Be Equal As Integers    ${gt}     ${g}
        Should Be Equal As Integers    ${bt}     ${b}
        Should Be Equal                ${ct}     ${c}
        Should Be Equal As Integers    ${at}     ${a}
        Should Be Equal As Integers    ${rft}    ${rf}
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]       Reinitialize Scenario   ${scenario}

2.6 Test Color Sensor Behavior On Computed Real Time Scenario
    [Tags]  ColorSensor

    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    color
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    color
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${sensor}       Create Object    ColorSensor  A
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        ${left}         Get From List      ${tests}[left]            ${i_step}
        ${right}        Get From List      ${tests}[right]           ${i_step}
        ${steering}     Get From List      ${tests}[steering]        ${i_step}
        ${speed}        Get From List      ${tests}[speed]           ${i_step}
        Start Scenario  ${scenario}
        # Turn 45°
        ${thread}           Start Method In A Thread    ${motor}    move    3.118030704    cm    100    50
        Sleep               0.2
        ${is_alive}         Is Thread Running    ${thread}
        Should Not Be True  ${is_alive}
        ${status}           Use Object Method  ${scenario}    status       True
        # Move to reach (60,60)
        ${thread}           Start Method In A Thread    ${motor}    move    84.85281374    cm    0      50
        Sleep               5
        ${is_alive}         Is Thread Running    ${thread}
        Should Not Be True  ${is_alive}
        ${status}           Use Object Method  ${scenario}    status       True
        # Reorient
        ${thread}           Start Method In A Thread    ${motor}    move    3.118030704    cm    -100   50
        Sleep               0.2
        ${is_alive}         Is Thread Running    ${thread}
        Should Not Be True  ${is_alive}
        ${status}           Use Object Method  ${scenario}    status       True
        # Start
        Use Object Method    ${motor}    start    False    -1    ${steering}    ${speed}
        Sleep                ${duration}
        Use Object Method    ${motor}    stop
        ${status}       Use Object Method  ${scenario}    status    True
        ${color}        Use Object Method  ${sensor}      get_color    True    None
        ${red}          Use Object Method  ${sensor}      get_red      True
        ${blue}         Use Object Method  ${sensor}      get_blue     True
        ${green}        Use Object Method  ${sensor}      get_green    True
        ${rt}           Get From List      ${tests}[red]      ${i_step}
        ${gt}           Get From List      ${tests}[green]    ${i_step}
        ${bt}           Get From List      ${tests}[blue]     ${i_step}
        ${ct}           Get From List      ${tests}[color]    ${i_step}
        Stop Scenario  ${scenario}
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reinitialize Scenario  ${scenario}

2.7 Test The Parallel Behaviour Of Wait Functions On Time Controlled Scenario
    [Tags]  ColorSensor
    ${scenario}         Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    color
    Start Scenario      ${scenario}
    ${sensor}           Create Object      ColorSensor    A
    Play Scenario During Steps  10
    ${thread}           Start Method In A Thread    ${sensor}    wait_until_color    red
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps  50
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps  30
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${c}        Use Object Method  ${sensor}    wait_for_new_color  True
    Should Be Equal     red    ${c}
    ${thread}           Start Method In A Thread    ${sensor}    wait_for_new_color
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Play Scenario During Steps  50
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${c}        Use Object Method  ${sensor}    get_color  True
    Should Be Equal     green    ${c}
    [Teardown]          Reinitialize Scenario   ${scenario}

2.8 Test The Parallel Behaviour Of Wait Functions On Real Time Scenario
    [Tags]  ColorSensor
    ${scenario}         Create Scenario    ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    color
    Start Scenario      ${scenario}
    ${sensor}           Create Object      ColorSensor    A
    Sleep               1
    ${thread}           Start Method In A Thread    ${sensor}    wait_until_color    red
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               5
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               3
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${c}        Use Object Method  ${sensor}    wait_for_new_color  True
    Should Be Equal     red    ${c}
    ${thread}           Start Method In A Thread    ${sensor}    wait_for_new_color
    ${is_alive}         Is Thread Running    ${thread}
    Should Be True      ${is_alive}
    Sleep               5
    ${is_alive}         Is Thread Running    ${thread}
    Should Not Be True  ${is_alive}
    ${c}        Use Object Method  ${sensor}    get_color  True
    Should Be Equal     green    ${c}
    [Teardown]          Reinitialize Scenario   ${scenario}

2.9 Test The Light Adjustment Functions And Their Impact On Color
    # No impact on color: when calling get_color, the sensor lights all its lights!
    [Tags]  ColorSensor
    ${scenario}         Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    color
    Start Scenario      ${scenario}
    ${sensor}           Create Object      ColorSensor    A
    Play Scenario During Steps  1
    ${c}                Use Object Method  ${sensor}    get_color  True
    Should Be Equal     white    ${c}
    Use Object Method  ${sensor}    light_up_all  False    -1    0
    Play Scenario During Steps  1
    ${c}                Use Object Method  ${sensor}    get_color  True
    Should Be Equal     white    ${c}
    Play Scenario During Steps  2
    ${c}                Use Object Method  ${sensor}    get_color  True
    Should Be Equal     white    ${c}
    Use Object Method  ${sensor}    light_up  False    -1    100    100    100
    Play Scenario During Steps  1
    ${c}                Use Object Method  ${sensor}    get_color  True
    Should Be Equal     white    ${c}
    [Teardown]          Reinitialize Scenario   ${scenario}
