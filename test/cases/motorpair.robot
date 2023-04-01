# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test spike motorpair mock
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------
*** Settings ***
Documentation   A test case to check motorpair mock functioning
Library         ../keywords/objects.py
Library         ../keywords/scenario.py
Library         ../keywords/dynamics.py
Library         Collections

*** Variables ***
${ROTC_JSON_CONF_FILE}           ${data}/rotc.json
${RORT_JSON_CONF_FILE}           ${data}/rort.json
${CPTC_JSON_CONF_FILE}           ${data}/cptc.json
${CPRT_JSON_CONF_FILE}           ${data}/cprt.json
${ROBOT_JSON_CONF_FILE}          ${data}/robot.json
${TEST_FILE}                     ${data}/dynamics.xlsm
${TIME_SPENT_LAUNCHING_COMMAND}  0.015

*** Test Cases ***

11.1 Ensure MotorPair Is Created With The Required Constants
    [Tags]  MotorPair
    ${scenario}     Create Scenario  ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    Start Scenario  ${scenario}
    ${motor}        Create Object    Motor         E
    ${motor}        Create Object    Motor         F
    ${motor}        Create Object    MotorPair     E     F
    @{members} =    Create List      move    start    stop    move_tank    start_tank    start_at_power    start_tank_at_power    get_default_speed    set_motor_rotation    set_default_speed    set_stop_action
    Should Have Members    ${motor}    ${members}
    [Teardown]      Reset Scenario   ${scenario}

11.2 Ensure Error Management Is Correctly Implemented
    [Tags]  MotorPair
    ${scenario}     Create Scenario  ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    Start Scenario  ${scenario}
    ${motor}        Create Object    Motor        E
    ${motor}        Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    Run Keyword And Expect Error     TypeError: amount is not a number                    Use Object Method  ${motor}     move                   False    -1    whatever    cm    0    100
    Run Keyword And Expect Error     TypeError: unit is not a string                      Use Object Method  ${motor}     move                   False    -1    180    100    0     100
    Run Keyword And Expect Error     ValueError: unit is not one of the allowed values    Use Object Method  ${motor}     move                   False    -1    180    whatever    0    100
    Run Keyword And Expect Error     TypeError: steering is not an integer                Use Object Method  ${motor}     move                   False    -1    100    cm    100.0  100
    Run Keyword And Expect Error     TypeError: speed is not an integer                   Use Object Method  ${motor}     move                   False    -1    100    cm    100    100.0
    Run Keyword And Expect Error     TypeError: steering is not an integer                Use Object Method  ${motor}     start                  False    -1    100.0  100
    Run Keyword And Expect Error     TypeError: speed is not an integer                   Use Object Method  ${motor}     start                  False    -1    100    100.0
    Run Keyword And Expect Error     TypeError: amount is not a number                    Use Object Method  ${motor}     move_tank              False    -1    whatever    cm    0    100
    Run Keyword And Expect Error     TypeError: unit is not a string                      Use Object Method  ${motor}     move_tank              False    -1    180    100    0     100
    Run Keyword And Expect Error     ValueError: unit is not one of the allowed values    Use Object Method  ${motor}     move_tank              False    -1    180    whatever    0    100
    Run Keyword And Expect Error     TypeError: left_speed is not an integer              Use Object Method  ${motor}     move_tank              False    -1    100    cm    100.0  100
    Run Keyword And Expect Error     TypeError: right_speed is not an integer             Use Object Method  ${motor}     move_tank              False    -1    100    cm    100    100.0
    Run Keyword And Expect Error     TypeError: left_speed is not an integer              Use Object Method  ${motor}     start_tank             False    -1    100.0  100
    Run Keyword And Expect Error     TypeError: right_speed is not an integer             Use Object Method  ${motor}     start_tank             False    -1    100    100.0
    Run Keyword And Expect Error     TypeError: power is not an integer                   Use Object Method  ${motor}     start_at_power         False    -1    100.0  100
    Run Keyword And Expect Error     TypeError: steering is not an integer                Use Object Method  ${motor}     start_at_power         False    -1    100    100.0
    Run Keyword And Expect Error     TypeError: left_power is not an integer              Use Object Method  ${motor}     start_tank_at_power    False    -1    100.0  100
    Run Keyword And Expect Error     TypeError: right_power is not an integer             Use Object Method  ${motor}     start_tank_at_power    False    -1    100    100.0
    Run Keyword And Expect Error     TypeError: amount is not a number                    Use Object Method  ${motor}     set_motor_rotation     False    -1    whatever    cm
    Run Keyword And Expect Error     TypeError: unit is not a string                      Use Object Method  ${motor}     set_motor_rotation     False    -1    180    100
    Run Keyword And Expect Error     ValueError: unit is not one of the allowed values    Use Object Method  ${motor}     set_motor_rotation     False    -1    180    whatever
    Run Keyword And Expect Error     TypeError: speed is not a number                     Use Object Method  ${motor}     set_default_speed      False    -1    100.0
    Run Keyword And Expect Error     TypeError: action is not a string                    Use Object Method  ${motor}     set_stop_action        False    -1    95.5
    Run Keyword And Expect Error     ValueError: action is not one of the allowed values  Use Object Method  ${motor}     set_stop_action        False    -1    whatever
    [Teardown]    Reset Scenario   ${scenario}

11.3 Test MotorPair Behavior On Read Only Time Controlled Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    Start Scenario  ${scenario}
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    @{steps} =      Create List      49        250      41
    @{degrees} =    Create List      64        389      443
    @{position} =   Create List      64        29       83
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${step}    IN    @{steps}
        Play Scenario During Steps     ${step}
        ${dl}       Use Object Method  ${left_motor}    get_degrees_counted    True
        ${pl}       Use Object Method  ${left_motor}    get_position  True
        ${dr}       Use Object Method  ${right_motor}   get_degrees_counted    True
        ${pr}       Use Object Method  ${right_motor}   get_position  True
        ${dt}       Get From List      ${degrees}           ${i_step}
        ${pt}       Get From List      ${position}          ${i_step}
        Should Be Equal As Integers    ${dt}     ${dr}
        Should Be Equal As Integers    ${pt}     ${pr}
        Should Be Equal As Integers    ${dt}     ${dl}
        Should Be Equal As Integers    ${pt}     ${pl}
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.4 Test MotorPair Move Behavior On Computed Time Controlled Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    move_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        ${left}         Get From List      ${tests}[left]            ${i_step}
        ${right}        Get From List      ${tests}[right]           ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${steering}     Get From List      ${tests}[steering]        ${i_step}
            ${speed}        Get From List      ${tests}[speed]           ${i_step}
            ${amount}       Get From List      ${tests}[amount]          ${i_step}
            ${steps}        Evaluate    ${duration} / 0.02 + 1
            Start Scenario  ${scenario}
            ${thread}       Start Method In A Thread    ${motor}    move    ${amount}    cm    ${steering}    ${speed}
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            Play Scenario During Steps  ${steps}
            Sleep                       1
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]           ${i_step}
            ${yt}       Get From List      ${tests}[y]           ${i_step}
            ${dt}       Get From List      ${tests}[direction]   ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.5 Test MotorPair Start/Stop Behavior On Computed Time Controlled Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]     ${i_step}
        ${east}        Get From List      ${tests}[east]      ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]       ${i_step}
        ${left}        Get From List      ${tests}[left]      ${i_step}
        ${right}       Get From List      ${tests}[right]     ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${steering}    Get From List      ${tests}[steering]  ${i_step}
            ${speed}       Get From List      ${tests}[speed]     ${i_step}
            ${steps}       Evaluate    ${duration} / 0.02 + 1
            Start Scenario  ${scenario}
            Use Object Method    ${motor}    start    False    -1    ${steering}    ${speed}
            Play Scenario During Steps  ${steps}
            Sleep                       1
            Use Object Method    ${motor}    stop
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]          ${i_step}
            ${yt}       Get From List      ${tests}[y]          ${i_step}
            ${dt}       Get From List      ${tests}[direction]  ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]  ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]  ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.6 Test MotorPair Start At Power/Stop Behavior On Computed Time Controlled Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]     ${i_step}
        ${east}        Get From List      ${tests}[east]      ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]       ${i_step}
        ${left}        Get From List      ${tests}[left]      ${i_step}
        ${right}       Get From List      ${tests}[right]     ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${steering}    Get From List      ${tests}[steering]  ${i_step}
            ${power}       Get From List      ${tests}[speed]     ${i_step}
            ${steps}       Evaluate    ${duration} / 0.02 + 1
            Start Scenario  ${scenario}
            Use Object Method    ${motor}    start_at_power    False    -1    ${power}    ${steering}
            Play Scenario During Steps  ${steps}
            Sleep                       1
            Use Object Method    ${motor}    stop
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]          ${i_step}
            ${yt}       Get From List      ${tests}[y]          ${i_step}
            ${dt}       Get From List      ${tests}[direction]  ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]  ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]  ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.7 Test MotorPair Move Tank Behavior On Computed Time Controlled Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    move_tank_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        ${left}         Get From List      ${tests}[left]            ${i_step}
        ${right}        Get From List      ${tests}[right]           ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${lspeed}       Get From List      ${tests}[left-command]    ${i_step}
            ${rspeed}       Get From List      ${tests}[right-command]   ${i_step}
            ${amount}       Get From List      ${tests}[amount]          ${i_step}
            ${steps}        Evaluate    ${duration} / 0.02 + 1
            Start Scenario  ${scenario}
            ${thread}       Start Method In A Thread    ${motor}    move_tank    ${amount}    cm    ${lspeed}    ${rspeed}
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            Play Scenario During Steps  ${steps}
            Sleep                       1
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]           ${i_step}
            ${yt}       Get From List      ${tests}[y]           ${i_step}
            ${dt}       Get From List      ${tests}[direction]   ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.8 Test MotorPair Start Tank/Stop Behavior On Computed Time Controlled Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_tank_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]     ${i_step}
        ${east}        Get From List      ${tests}[east]      ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]       ${i_step}
        ${left}        Get From List      ${tests}[left]      ${i_step}
        ${right}       Get From List      ${tests}[right]     ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${lspeed}      Get From List      ${tests}[left-command]    ${i_step}
            ${rspeed}      Get From List      ${tests}[right-command]   ${i_step}
            ${steps}       Evaluate    ${duration} / 0.02 + 1
            Start Scenario  ${scenario}
            Use Object Method    ${motor}    start_tank   False    -1    ${lspeed}    ${rspeed}
            Play Scenario During Steps  ${steps}
            Sleep                       1
            Use Object Method    ${motor}    stop
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]          ${i_step}
            ${yt}       Get From List      ${tests}[y]          ${i_step}
            ${dt}       Get From List      ${tests}[direction]  ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]  ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]  ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.9 Test MotorPair Start Tank At Power/Stop Behavior On Computed Time Controlled Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_tank_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]     ${i_step}
        ${east}        Get From List      ${tests}[east]      ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]       ${i_step}
        ${left}        Get From List      ${tests}[left]      ${i_step}
        ${right}       Get From List      ${tests}[right]     ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${lspeed}      Get From List      ${tests}[left-command]    ${i_step}
            ${rspeed}      Get From List      ${tests}[right-command]   ${i_step}
            ${steps}       Evaluate    ${duration} / 0.02 + 1
            Start Scenario  ${scenario}
            Use Object Method    ${motor}    start_tank_at_power    False    -1    ${lspeed}    ${rspeed}
            Play Scenario During Steps  ${steps}
            Sleep                       1
            Use Object Method    ${motor}    stop
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]          ${i_step}
            ${yt}       Get From List      ${tests}[y]          ${i_step}
            ${dt}       Get From List      ${tests}[direction]  ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]  ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]  ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.10 Test MotorPair Behavior On Read Only Real Time Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    @{steps} =      Create List      4.9       25       4.1
    @{degrees} =    Create List      64        389      443
    @{position} =   Create List      64        29       83
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    ${previous_time} =  Get Time Milliseconds
    Start Scenario      ${scenario}
    FOR    ${step}    IN    @{steps}
        ${current_time} =    Get Time Milliseconds
        ${delta_time} =      Evaluate    ${step} - ${current_time} + ${previous_time}
        Sleep       ${delta_time}
        ${previous_time} =   Get Time Milliseconds
        ${dl}       Use Object Method  ${left_motor}    get_degrees_counted    True
        ${pl}       Use Object Method  ${left_motor}    get_position  True
        ${dr}       Use Object Method  ${right_motor}   get_degrees_counted    True
        ${pr}       Use Object Method  ${right_motor}   get_position  True
        ${dt}       Get From List      ${degrees}       ${i_step}
        ${pt}       Get From List      ${position}      ${i_step}
        Should Be Equal As Numbers With Precision    ${dt}     ${dr}    1
        Should Be Equal As Numbers With Precision    ${pt}     ${pr}    1
        Should Be Equal As Numbers With Precision    ${dt}     ${dl}    1
        Should Be Equal As Numbers With Precision    ${pt}     ${pl}    1
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.11 Test MotorPair Move Behavior On Computed Real Time Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    move_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        ${left}         Get From List      ${tests}[left]            ${i_step}
        ${right}        Get From List      ${tests}[right]           ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${steering}     Get From List      ${tests}[steering]        ${i_step}
            ${speed}        Get From List      ${tests}[speed]           ${i_step}
            ${amount}       Get From List      ${tests}[amount]          ${i_step}
            Start Scenario  ${scenario}
            ${thread}       Start Method In A Thread    ${motor}    move    ${amount}    cm    ${steering}    ${speed}
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            Sleep               ${duration}
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]           ${i_step}
            ${yt}       Get From List      ${tests}[y]           ${i_step}
            ${dt}       Get From List      ${tests}[direction]   ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.12 Test MotorPair Start/Stop Behavior On Computed Real Time Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        ${left}         Get From List      ${tests}[left]            ${i_step}
        ${right}        Get From List      ${tests}[right]           ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${steering}     Get From List      ${tests}[steering]        ${i_step}
            ${speed}        Get From List      ${tests}[speed]           ${i_step}
            Start Scenario  ${scenario}
            Use Object Method    ${motor}    start    False    -1    ${steering}    ${speed}
            Sleep                ${duration}
            Use Object Method    ${motor}    stop
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]           ${i_step}
            ${yt}       Get From List      ${tests}[y]           ${i_step}
            ${dt}       Get From List      ${tests}[direction]   ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.13 Test MotorPair Start At Power/Stop Behavior On Computed Real Time Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        ${left}         Get From List      ${tests}[left]            ${i_step}
        ${right}        Get From List      ${tests}[right]           ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${steering}     Get From List      ${tests}[steering]        ${i_step}
            ${power}        Get From List      ${tests}[speed]           ${i_step}
            Start Scenario  ${scenario}
            Use Object Method   ${motor}    start_at_power    False     -1    ${power}    ${steering}
            Sleep               ${duration}
            Use Object Method   ${motor}    stop
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]           ${i_step}
            ${yt}       Get From List      ${tests}[y]           ${i_step}
            ${dt}       Get From List      ${tests}[direction]   ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.14 Test MotorPair Move Tank Behavior On Computed Real Time Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    move_tank_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        ${left}         Get From List      ${tests}[left]            ${i_step}
        ${right}        Get From List      ${tests}[right]           ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${lspeed}       Get From List      ${tests}[left-command]    ${i_step}
            ${rspeed}       Get From List      ${tests}[right-command]   ${i_step}
            ${amount}       Get From List      ${tests}[amount]          ${i_step}
            Start Scenario  ${scenario}
            ${thread}       Start Method In A Thread    ${motor}    move_tank   ${amount}    cm    ${lspeed}    ${rspeed}
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            Sleep               ${duration}
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]           ${i_step}
            ${yt}       Get From List      ${tests}[y]           ${i_step}
            ${dt}       Get From List      ${tests}[direction]   ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.15 Test MotorPair Start Tank/Stop Behavior On Computed Real Time Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_tank_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        ${left}         Get From List      ${tests}[left]            ${i_step}
        ${right}        Get From List      ${tests}[right]           ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${lspeed}       Get From List      ${tests}[left-command]    ${i_step}
            ${rspeed}       Get From List      ${tests}[right-command]   ${i_step}
            Start Scenario  ${scenario}
            Use Object Method   ${motor}    start_tank    False    -1    ${lspeed}    ${rspeed}
            Sleep               ${duration}
            Use Object Method   ${motor}    stop
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]           ${i_step}
            ${yt}       Get From List      ${tests}[y]           ${i_step}
            ${dt}       Get From List      ${tests}[direction]   ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

11.16 Test MotorPair Start Tank At Power/Stop Behavior On Computed Real Time Scenario
    [Tags]    MotorPair
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_tank_pair
    ${left_motor}   Create Object    Motor        E
    ${right_motor}  Create Object    Motor        F
    ${motor}        Create Object    MotorPair    E     F
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        ${left}         Get From List      ${tests}[left]            ${i_step}
        ${right}        Get From List      ${tests}[right]           ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0 and "${left}" == "E"
            ${lpower}       Get From List      ${tests}[left-command]    ${i_step}
            ${rpower}       Get From List      ${tests}[right-command]   ${i_step}
            Start Scenario  ${scenario}
            Use Object Method   ${motor}    start_tank_at_power    False    -1    ${lpower}    ${rpower}
            Sleep               ${duration}
            Use Object Method   ${motor}    stop
            ${status}       Use Object Method  ${scenario}    status    True
            ${e_degrees}    Use Object Method  ${left_motor}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${right_motor}     get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]           ${i_step}
            ${yt}       Get From List      ${tests}[y]           ${i_step}
            ${dt}       Get From List      ${tests}[direction]   ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
            Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
            Should Be Equal As Numbers With Precision     ${e_degrees}                            ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}                            ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

