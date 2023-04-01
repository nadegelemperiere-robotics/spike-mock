# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test spike motor mock
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

*** Settings ***
Documentation   A test case to check motor mock functioning
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

10.1 Ensure Motor Is Created With The Required Constants
    [Tags]  Motor
    ${scenario}        Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    Start Scenario     ${scenario}
    ${motor}           Create Object      Motor    E
    @{members} =       Create List        run_to_position    run_to_degrees_counted    run_for_degrees    run_for_rotations    run_for_seconds    start    stop    start_at_power    get_speed    get_position    get_degrees_counted    get_default_speed    was_interrupted    was_stalled    set_degrees_counted    set_default_speed    set_stop_action    set_stall_detection
    Should Have Members    ${motor}    ${members}
    [Teardown]         Reset Scenario   ${scenario}

10.2 Ensure Error Management Is Correctly Implemented
    [Tags]    Motor
    ${scenario}        Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    Start Scenario     ${scenario}
    ${motor}           Create Object      Motor    E
    Run Keyword And Expect Error    TypeError: degrees is not an integer                       Use Object Method  ${motor}     run_to_position         False    -1    180.5     shortest path    100
    Run Keyword And Expect Error    TypeError: direction is not a string                       Use Object Method  ${motor}     run_to_position         False    -1    180       100              100
    Run Keyword And Expect Error    TypeError: speed is not an integer                         Use Object Method  ${motor}     run_to_position         False    -1    180       shortest path    95.5
    Run Keyword And Expect Error    ValueError: direction is none of the allowed values        Use Object Method  ${motor}     run_to_position         False    -1    180       whatever         100
    Run Keyword And Expect Error    ValueError: degrees are not in the range 0-359             Use Object Method  ${motor}     run_to_position         False    -1    360       shortest path    100
    Run Keyword And Expect Error    ValueError: degrees are not in the range 0-359             Use Object Method  ${motor}     run_to_position         False    -1    -1        shortest path    100
    Run Keyword And Expect Error    TypeError: degrees is not an integer                       Use Object Method  ${motor}     run_to_degrees_counted  False    -1    95.5      100
    Run Keyword And Expect Error    TypeError: speed is not an integer                         Use Object Method  ${motor}     run_to_degrees_counted  False    -1    180       95.5
    Run Keyword And Expect Error    TypeError: degrees is not an integer                       Use Object Method  ${motor}     run_for_degrees         False    -1    95.5      100
    Run Keyword And Expect Error    TypeError: speed is not an integer                         Use Object Method  ${motor}     run_for_degrees         False    -1    180       95.5
    Run Keyword And Expect Error    TypeError: rotations is not a number                       Use Object Method  ${motor}     run_for_rotations       False    -1    whatever  100
    Run Keyword And Expect Error    TypeError: speed is not an integer                         Use Object Method  ${motor}     run_for_rotations       False    -1    180       95.5
    Run Keyword And Expect Error    TypeError: seconds is not a number                         Use Object Method  ${motor}     run_for_seconds         False    -1    whatever  100
    Run Keyword And Expect Error    TypeError: speed is not an integer                         Use Object Method  ${motor}     run_for_seconds         False    -1    180       95.5
    Run Keyword And Expect Error    TypeError: speed is not an integer                         Use Object Method  ${motor}     start                   False    -1    95.5
    Run Keyword And Expect Error    TypeError: power is not an integer                         Use Object Method  ${motor}     start_at_power          False    -1    95.5
    Run Keyword And Expect Error    TypeError: degrees_counted is not an integer               Use Object Method  ${motor}     set_degrees_counted     False    -1    95.5
    Run Keyword And Expect Error    TypeError: speed is not an integer                         Use Object Method  ${motor}     set_default_speed       False    -1    95.5
    Run Keyword And Expect Error    TypeError: action is not a string                          Use Object Method  ${motor}     set_stop_action         False    -1    95.5
    Run Keyword And Expect Error    ValueError: action is not in the list of allowed values    Use Object Method  ${motor}     set_stop_action         False    -1    whatever
    Run Keyword And Expect Error    TypeError: stop_when_stalled is not a boolean              Use Object Method  ${motor}     set_stall_detection     False    -1    100
    [Teardown]         Reset Scenario   ${scenario}

10.3 Test Motor Behavior On Read Only Time Controlled Scenario
    [Tags]    Motor
    ${scenario}        Create Scenario    ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    Start Scenario     ${scenario}
    ${motor}           Create Object      Motor    E
    @{steps} =         Create List    49        250      41
    @{degrees} =       Create List    64        389      443
    @{position} =      Create List    64        29       83
    ${i_step} =        Set Variable   0
    ${i_step} =        Convert To Integer  ${i_step}
    FOR    ${step}    IN    @{steps}
        Play Scenario During Steps     ${step}
        Sleep                          1
        ${d}        Use Object Method  ${motor}    get_degrees_counted    True
        ${p}        Use Object Method  ${motor}    get_position  True
        ${dt}       Get From List      ${degrees}           ${i_step}
        ${pt}       Get From List      ${position}          ${i_step}
        Should Be Equal As Integers    ${dt}     ${d}
        Should Be Equal As Integers    ${pt}     ${p}
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]         Reset Scenario   ${scenario}

10.4 Test Motor Run For Degrees Behavior On Computed Time Controlled Scenario
    [Tags]    Motor
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_for_degrees
    ${motore}       Create Object    Motor        E
    ${motorf}       Create Object    Motor        F
    ${motord}       Create Object    Motor        D
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0
            ${port}        Get From List      ${tests}[port]            ${i_step}
            ${speed}       Get From List      ${tests}[speed]           ${i_step}
            ${degrees}     Get From List      ${tests}[degrees]         ${i_step}
            ${steps}       Evaluate    ${duration} / 0.02 + 1
            Start Scenario  ${scenario}
            IF        "${port}" == "E"
                ${thread}       Start Method In A Thread    ${motore}    run_for_degrees    ${degrees}    ${speed}
            ELSE IF    "${port}" == "F"
                ${thread}       Start Method In A Thread    ${motorf}    run_for_degrees    ${degrees}    ${speed}
            ELSE IF    "${port}" == "D"
                ${thread}       Start Method In A Thread    ${motord}    run_for_degrees    ${degrees}    ${speed}
            END
            ${is_alive}                 Is Thread Running    ${thread}
            Should Be True              ${is_alive}
            Play Scenario During Steps  ${steps}
            Sleep                       1
            ${is_alive}                 Is Thread Running    ${thread}
            Should Not Be True          ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${d_degrees}    Use Object Method  ${motord}      get_degrees_counted    True
            ${e_degrees}    Use Object Method  ${motore}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${motorf}      get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]               ${i_step}
            ${yt}       Get From List      ${tests}[y]               ${i_step}
            ${dt}       Get From List      ${tests}[direction]       ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
            ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]         ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]         ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]       ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]     0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]      0        0.01
            Should Be Equal As Numbers With Precision     ${d_degrees}         ${ot}    10
            Should Be Equal As Numbers With Precision     ${e_degrees}         ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}         ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

10.5 Test Motor Run For Rotations Behavior On Computed Time Controlled Scenario
    [Tags]    Motor
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_for_degrees
    ${motore}       Create Object    Motor        E
    ${motorf}       Create Object    Motor        F
    ${motord}       Create Object    Motor        D
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0
            ${port}        Get From List      ${tests}[port]            ${i_step}
            ${speed}       Get From List      ${tests}[speed]           ${i_step}
            ${degrees}     Get From List      ${tests}[degrees]         ${i_step}
            ${rotations}   Evaluate     ${degrees} * 1.0/360
            ${rotations}   Convert To String    ${rotations}
            ${steps}       Evaluate    ${duration} / 0.02 + 1
            Start Scenario  ${scenario}
            IF        "${port}" == "E"
                ${thread}       Start Method In A Thread    ${motore}    run_for_rotations    ${rotations}    ${speed}
            ELSE IF    "${port}" == "F"
                ${thread}       Start Method In A Thread    ${motorf}    run_for_rotations    ${rotations}    ${speed}
            ELSE IF    "${port}" == "D"
                ${thread}       Start Method In A Thread    ${motord}    run_for_rotations    ${rotations}    ${speed}
            END
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            Play Scenario During Steps  ${steps}
            Sleep                       1
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${d_degrees}    Use Object Method  ${motord}      get_degrees_counted    True
            ${e_degrees}    Use Object Method  ${motore}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${motorf}      get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]               ${i_step}
            ${yt}       Get From List      ${tests}[y]               ${i_step}
            ${dt}       Get From List      ${tests}[direction]       ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
            ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]             ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]             ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]           ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]         0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]          0        0.01
            Should Be Equal As Numbers With Precision     ${d_degrees}             ${ot}    10
            Should Be Equal As Numbers With Precision     ${e_degrees}             ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}             ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

10.6 Test Motor Run For Seconds Behavior On Computed Time Controlled Scenario
    [Tags]    Motor
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_for_seconds
    ${motore}       Create Object    Motor        E
    ${motorf}       Create Object    Motor        F
    ${motord}       Create Object    Motor        D
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0
            ${port}        Get From List      ${tests}[port]            ${i_step}
            ${speed}       Get From List      ${tests}[speed]           ${i_step}
            ${degrees}     Get From List      ${tests}[degrees]         ${i_step}
            ${steps}       Evaluate    ${duration} / 0.02 + 1
            Start Scenario  ${scenario}
            IF        "${port}" == "E"
                ${thread}       Start Method In A Thread    ${motore}    run_for_seconds    ${duration}    ${speed}
            ELSE IF    "${port}" == "F"
                ${thread}       Start Method In A Thread    ${motorf}    run_for_seconds    ${duration}    ${speed}
            ELSE IF    "${port}" == "D"
                ${thread}       Start Method In A Thread    ${motord}    run_for_seconds    ${duration}    ${speed}
            END
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            Play Scenario During Steps  ${steps}
            Sleep                       1
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${d_degrees}    Use Object Method  ${motord}      get_degrees_counted    True
            ${e_degrees}    Use Object Method  ${motore}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${motorf}      get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]               ${i_step}
            ${yt}       Get From List      ${tests}[y]               ${i_step}
            ${dt}       Get From List      ${tests}[direction]       ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
            ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]             ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]             ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]           ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]         0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]          0        0.01
            Should Be Equal As Numbers With Precision     ${d_degrees}             ${ot}    10
            Should Be Equal As Numbers With Precision     ${e_degrees}             ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}             ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

10.7 Test Motor Run To Position Behavior On Computed Time Controlled Scenario
    [Tags]    Motor
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_to_position
    ${motore}       Create Object    Motor        E
    ${motorf}       Create Object    Motor        F
    ${motord}       Create Object    Motor        D
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0
            ${port}        Get From List      ${tests}[port]         ${i_step}
            ${speed}       Get From List      ${tests}[speed]        ${i_step}
            ${degrees}     Get From List      ${tests}[degrees]      ${i_step}
            ${direction}   Get From List      ${tests}[dir]          ${i_step}
            ${steps}       Evaluate    ${duration} / 0.02 + 3
            Start Scenario  ${scenario}
            IF        "${port}" == "E"
                ${thread1}       Start Method In A Thread    ${motore}    run_for_degrees   1021    50
                ${is_alive}      Is Thread Running      ${thread1}
                WHILE    ${is_alive}   limit=1300
                    Play Scenario During Steps  10
                    ${is_alive}  Is Thread Running      ${thread1}
                END
                ${status}       Use Object Method  ${scenario}    status    True
                ${thread}        Start Method In A Thread    ${motore}    run_to_position    ${degrees}    ${direction}    ${speed}
            ELSE IF    "${port}" == "F"
                ${thread1}        Start Method In A Thread   ${motorf}    run_for_degrees   1021    50
                ${is_alive}      Is Thread Running      ${thread1}
                WHILE    ${is_alive}   limit=1300
                    Play Scenario During Steps  10
                    ${is_alive}  Is Thread Running      ${thread1}
                END
                ${status}       Use Object Method  ${scenario}    status    True
                ${thread}       Start Method In A Thread    ${motorf}    run_to_position    ${degrees}    ${direction}    ${speed}
            ELSE IF    "${port}" == "D"
                ${thread1}       Start Method In A Thread   ${motord}    run_for_degrees   1021    50
                ${is_alive}      Is Thread Running      ${thread1}
                WHILE    ${is_alive}   limit=1300
                    Play Scenario During Steps  10
                    ${is_alive}  Is Thread Running      ${thread1}
                END
                ${status}       Use Object Method  ${scenario}    status    True
                ${thread}       Start Method In A Thread    ${motord}    run_to_position    ${degrees}    ${direction}    ${speed}
            END
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            Play Scenario During Steps  ${steps}
            Sleep                       1
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${d_degrees}    Use Object Method  ${motord}      get_degrees_counted    True
            ${e_degrees}    Use Object Method  ${motore}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${motorf}      get_degrees_counted    True
            IF         "${port}" == "E"
                ${position}    Use Object Method  ${motore}      get_position    True
            ELSE IF    "${port}" == "F"
                ${position}    Use Object Method  ${motorf}      get_position    True
            ELSE IF    "${port}" == "D"
                ${position}    Use Object Method  ${motord}      get_position    True
            END
            ${xt}       Get From List      ${tests}[x]               ${i_step}
            ${yt}       Get From List      ${tests}[y]               ${i_step}
            ${dt}       Get From List      ${tests}[direction]       ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
            ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
            ${pt}       Get From List      ${tests}[degrees]         ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]             ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]             ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]           ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]         0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]          0        0.01
            Should Be Equal As Numbers With Precision     ${d_degrees}             ${ot}    16
            Should Be Equal As Numbers With Precision     ${e_degrees}             ${lt}    16
            Should Be Equal As Numbers With Precision     ${f_degrees}             ${rt}    16
            Should Be Equal As Angles With Precision      ${position}              ${pt}    16
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

10.8 Test Motor Start At Power/Stop Behavior On Computed Time Controlled Scenario
    [Tags]    Motor
    ${scenario}     Create Scenario  ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_single
    ${motore}       Create Object    Motor        E
    ${motorf}       Create Object    Motor        F
    ${motord}       Create Object    Motor        D
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0
            ${port}        Get From List      ${tests}[port]            ${i_step}
            ${speed}       Get From List      ${tests}[speed]           ${i_step}
            ${steps}       Evaluate    ${duration} / 0.02 + 1
            Start Scenario  ${scenario}
            IF    "${port}" == "E"
                Use Object Method    ${motore}    start_at_power    False    -1    ${speed}
            ELSE IF    "${port}" == "F"
                Use Object Method    ${motorf}    start_at_power    False    -1    ${speed}
            ELSE IF    "${port}" == "D"
                Use Object Method    ${motord}    start_at_power    False    -1    ${speed}
            END
            Play Scenario During Steps  ${steps}
            Sleep                       1
            IF        "${port}" == "E"
                Use Object Method    ${motore}    stop    False    -1
            ELSE IF    "${port}" == "F"
                Use Object Method    ${motorf}    stop    False    -1
            ELSE IF    "${port}" == "D"
                Use Object Method    ${motord}    stop    False    -1
            END
            ${status}       Use Object Method  ${scenario}    status    True
            ${d_degrees}    Use Object Method  ${motord}      get_degrees_counted    True
            ${e_degrees}    Use Object Method  ${motore}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${motorf}      get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]               ${i_step}
            ${yt}       Get From List      ${tests}[y]               ${i_step}
            ${dt}       Get From List      ${tests}[direction]       ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
            ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]             ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]             ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]           ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]         0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]          0        0.01
            Should Be Equal As Numbers With Precision     ${d_degrees}             ${ot}    10
            Should Be Equal As Numbers With Precision     ${e_degrees}             ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}             ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

10.9 Test Motor Behavior On Read Only Real Time Scenario
    [Tags]    Motor
    ${scenario}        Create Scenario    ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    @{steps} =         Create List    4.9       25       4.1
    @{degrees} =       Create List    64        389      443
    @{position} =      Create List    64        29       83
    ${i_step} =        Set Variable   0
    ${i_step} =        Convert To Integer  ${i_step}
    ${previous_time} =      Get Time Milliseconds
    Start Scenario      ${scenario}
    ${motor}           Create Object      Motor    E
    FOR    ${step}    IN    @{steps}
        ${current_time} =    Get Time Milliseconds
        ${delta_time} =      Evaluate    ${step} - ${current_time} + ${previous_time}
        Sleep       ${delta_time}
        ${previous_time} =   Get Time Milliseconds
        ${d}        Use Object Method  ${motor}    get_degrees_counted    True
        ${p}        Use Object Method  ${motor}    get_position  True
        ${dt}       Get From List      ${degrees}           ${i_step}
        ${pt}       Get From List      ${position}          ${i_step}
        Should Be Equal As Numbers With Precision     ${dt}     ${d}    1
        Should Be Equal As Numbers With Precision     ${pt}     ${p}    1
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]         Reset Scenario   ${scenario}

10.10 Test Motor Run For Degrees Behavior On Computed Real Time Scenario
    [Tags]    Motor
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_for_degrees
    ${motore}       Create Object    Motor        E
    ${motorf}       Create Object    Motor        F
    ${motord}       Create Object    Motor        D
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0
            ${port}        Get From List      ${tests}[port]            ${i_step}
            ${speed}       Get From List      ${tests}[speed]           ${i_step}
            ${degrees}     Get From List      ${tests}[degrees]         ${i_step}
            Start Scenario  ${scenario}
            IF        "${port}" == "E"
                ${thread}       Start Method In A Thread    ${motore}    run_for_degrees    ${degrees}    ${speed}
            ELSE IF    "${port}" == "F"
                ${thread}       Start Method In A Thread    ${motorf}    run_for_degrees    ${degrees}    ${speed}
            ELSE IF    "${port}" == "D"
                ${thread}       Start Method In A Thread    ${motord}    run_for_degrees    ${degrees}    ${speed}
            END
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            ${duration}         Evaluate     ${duration} + 0.1
            ${duration}         Convert To String    ${duration}
            Sleep               ${duration}
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${d_degrees}    Use Object Method  ${motord}      get_degrees_counted    True
            ${e_degrees}    Use Object Method  ${motore}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${motorf}      get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]               ${i_step}
            ${yt}       Get From List      ${tests}[y]               ${i_step}
            ${dt}       Get From List      ${tests}[direction]       ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
            ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]             ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]             ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]           ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]         0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]          0        0.01
            Should Be Equal As Numbers With Precision     ${d_degrees}             ${ot}    10
            Should Be Equal As Numbers With Precision     ${e_degrees}             ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}             ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

10.11 Test Motor Run For Rotations Behavior On Computed Real Time Scenario
    [Tags]    Motor
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_for_degrees
    ${motore}       Create Object    Motor        E
    ${motorf}       Create Object    Motor        F
    ${motord}       Create Object    Motor        D
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0
            ${port}        Get From List      ${tests}[port]            ${i_step}
            ${speed}       Get From List      ${tests}[speed]           ${i_step}
            ${degrees}     Get From List      ${tests}[degrees]         ${i_step}
            ${rotations}   Evaluate     ${degrees} * 1.0/360
            ${rotations}   Convert To String    ${rotations}
            Start Scenario  ${scenario}
            IF        "${port}" == "E"
                ${thread}       Start Method In A Thread    ${motore}    run_for_rotations    ${rotations}    ${speed}
            ELSE IF    "${port}" == "F"
                ${thread}       Start Method In A Thread    ${motorf}    run_for_rotations    ${rotations}    ${speed}
            ELSE IF    "${port}" == "D"
                ${thread}       Start Method In A Thread    ${motord}    run_for_rotations    ${rotations}    ${speed}
            END
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            ${duration}         Evaluate     ${duration} + 0.1
            ${duration}         Convert To String    ${duration}
            Sleep               ${duration}
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${d_degrees}    Use Object Method  ${motord}      get_degrees_counted    True
            ${e_degrees}    Use Object Method  ${motore}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${motorf}      get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]               ${i_step}
            ${yt}       Get From List      ${tests}[y]               ${i_step}
            ${dt}       Get From List      ${tests}[direction]       ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
            ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]             ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]             ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]           ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]         0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]          0        0.01
            Should Be Equal As Numbers With Precision     ${d_degrees}             ${ot}    10
            Should Be Equal As Numbers With Precision     ${e_degrees}             ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}             ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

10.12 Test Motor Run For Seconds Behavior On Computed Real Time Scenario
    [Tags]    Motor
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_for_seconds
    ${motore}       Create Object    Motor        E
    ${motorf}       Create Object    Motor        F
    ${motord}       Create Object    Motor        D
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0
            ${port}        Get From List      ${tests}[port]            ${i_step}
            ${speed}       Get From List      ${tests}[speed]           ${i_step}
            ${degrees}     Get From List      ${tests}[degrees]         ${i_step}
            Start Scenario  ${scenario}
            IF        "${port}" == "E"
                ${thread}       Start Method In A Thread    ${motore}    run_for_seconds    ${duration}    ${speed}
            ELSE IF    "${port}" == "F"
                ${thread}       Start Method In A Thread    ${motorf}    run_for_seconds    ${duration}    ${speed}
            ELSE IF    "${port}" == "D"
                ${thread}       Start Method In A Thread    ${motord}    run_for_seconds    ${duration}    ${speed}
            END
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            ${duration}         Evaluate     ${duration} + 0.1
            ${duration}         Convert To String    ${duration}
            Sleep               ${duration}
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${d_degrees}    Use Object Method  ${motord}      get_degrees_counted    True
            ${e_degrees}    Use Object Method  ${motore}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${motorf}      get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]               ${i_step}
            ${yt}       Get From List      ${tests}[y]               ${i_step}
            ${dt}       Get From List      ${tests}[direction]       ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
            ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]             ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]             ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]           ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]         0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]          0        0.01
            Should Be Equal As Numbers With Precision     ${d_degrees}             ${ot}    10
            Should Be Equal As Numbers With Precision     ${e_degrees}             ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}             ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

10.13 Test Motor Run To Position Behavior On Computed Real Time Scenario
    [Tags]    Motor
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_to_position
    ${motore}       Create Object    Motor        E
    ${motorf}       Create Object    Motor        F
    ${motord}       Create Object    Motor        D
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0
            ${port}        Get From List      ${tests}[port]         ${i_step}
            ${speed}       Get From List      ${tests}[speed]        ${i_step}
            ${degrees}     Get From List      ${tests}[degrees]      ${i_step}
            ${direction}   Get From List      ${tests}[dir]          ${i_step}
            Start Scenario  ${scenario}
            IF        "${port}" == "E"
                Use Object Method    ${motore}    run_for_degrees   False    -1    1021    50
                ${thread}       Start Method In A Thread    ${motore}    run_to_position    ${degrees}    ${direction}    ${speed}
            ELSE IF    "${port}" == "F"
                Use Object Method    ${motorf}    run_for_degrees   False    -1    1021    50
                ${thread}       Start Method In A Thread    ${motorf}    run_to_position    ${degrees}    ${direction}    ${speed}
            ELSE IF    "${port}" == "D"
                Use Object Method    ${motord}    run_for_degrees   False    -1    1021    50
                ${thread}       Start Method In A Thread    ${motord}    run_to_position    ${degrees}    ${direction}    ${speed}
            END
            ${is_alive}         Is Thread Running    ${thread}
            Should Be True      ${is_alive}
            ${duration}         Evaluate     ${duration} + 0.1
            ${duration}         Convert To String    ${duration}
            Sleep               ${duration}
            ${is_alive}         Is Thread Running    ${thread}
            Should Not Be True  ${is_alive}
            ${status}       Use Object Method  ${scenario}    status    True
            ${d_degrees}    Use Object Method  ${motord}      get_degrees_counted    True
            ${e_degrees}    Use Object Method  ${motore}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${motorf}      get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]               ${i_step}
            ${yt}       Get From List      ${tests}[y]               ${i_step}
            ${dt}       Get From List      ${tests}[direction]       ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
            ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]             ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]             ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]           ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]         0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]          0        0.01
            Should Be Equal As Numbers With Precision     ${d_degrees}             ${ot}    10
            Should Be Equal As Numbers With Precision     ${e_degrees}             ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}             ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}

10.14 Test Motor Start At Power/Stop Behavior On Computed Real Time Scenario
    [Tags]    Motor
    ${scenario}     Create Scenario  ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}    motors
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_single
    ${motore}       Create Object    Motor        E
    ${motorf}       Create Object    Motor        F
    ${motord}       Create Object    Motor        D
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}        Get From List      ${tests}[north]           ${i_step}
        ${east}         Get From List      ${tests}[east]            ${i_step}
        ${yaw}          Get From List      ${tests}[yaw]             ${i_step}
        IF    ${north} == 0 and ${east} == 0 and ${yaw} == 0
            ${port}        Get From List      ${tests}[port]            ${i_step}
            ${speed}       Get From List      ${tests}[speed]           ${i_step}
            Start Scenario  ${scenario}
            IF    "${port}" == "E"
                Use Object Method    ${motore}    start_at_power    False    -1    ${speed}
            ELSE IF    "${port}" == "F"
                Use Object Method    ${motorf}    start_at_power    False    -1    ${speed}
            ELSE IF    "${port}" == "D"
                Use Object Method    ${motord}    start_at_power    False    -1    ${speed}
            END
            ${duration}         Evaluate     ${duration}
            ${duration}         Convert To String    ${duration}
            Sleep               ${duration}
            IF        "${port}" == "E"
                Use Object Method    ${motore}    stop    False    -1
            ELSE IF    "${port}" == "F"
                Use Object Method    ${motorf}    stop    False    -1
            ELSE IF    "${port}" == "D"
                Use Object Method    ${motord}    stop    False    -1
            END
            ${status}       Use Object Method  ${scenario}    status    True
            ${d_degrees}    Use Object Method  ${motord}      get_degrees_counted    True
            ${e_degrees}    Use Object Method  ${motore}      get_degrees_counted    True
            ${f_degrees}    Use Object Method  ${motorf}      get_degrees_counted    True
            ${xt}       Get From List      ${tests}[x]               ${i_step}
            ${yt}       Get From List      ${tests}[y]               ${i_step}
            ${dt}       Get From List      ${tests}[direction]       ${i_step}
            ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
            ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
            ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
            Should Be Equal As Numbers With Precision     ${status}[x]             ${xt}    0.4
            Should Be Equal As Numbers With Precision     ${status}[y]             ${yt}    0.4
            Should Be Equal As Angles With Precision      ${status}[yaw]           ${dt}    10
            Should Be Equal As Angles With Precision      ${status}[pitch]         0        0.01
            Should Be Equal As Angles With Precision      ${status}[roll]          0        0.01
            Should Be Equal As Numbers With Precision     ${d_degrees}             ${ot}    10
            Should Be Equal As Numbers With Precision     ${e_degrees}             ${lt}    10
            Should Be Equal As Numbers With Precision     ${f_degrees}             ${rt}    10
            Stop Scenario  ${scenario}
        END
        ${i_step} =     Set Variable   ${i_step + 1}
    END
    [Teardown]      Reset Scenario  ${scenario}
