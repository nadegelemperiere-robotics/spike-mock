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
Documentation   A test case to check robot dynamics
Library         ../keywords/objects.py
Library         ../keywords/dynamics.py
Library         Collections

*** Variables ***
${ROBOT_JSON_CONF_FILE}     ${data}/robot.json
${TEST_FILE}                ${data}/dynamics.xlsm

*** Test Cases ***
5.1 Ensure Robot Parts Are Correctly Positioned in NED Coordinates
    [Tags]          Dynamics
    ${model}        Create Model     ${ROBOT_JSON_CONF_FILE}
    ${dynamics}     Create Dynamics  ${model}    0    0    0
    ${current}      Use Object Method     ${dynamics}    current    True
    @{ports} =      Create List      E           F           E          F           D         A            B            C
    @{type} =       Create List      Wheel       Wheel       Motor      Motor       Motor     ColorSensor  ForceSensor  DistanceSensor
    @{index} =      Create List      0           0           0          0           0         0            0            0
    @{x} =          Create List      0           0           0          0           8.8       4            4.800947     10.4
    @{y} =          Create List      -3.978000   3.978000   -1.592484   1.592484    -4        -4           3.912480     -0.007520
    @{z} =          Create List      -1.6        -1.6       -1.6        -1.6        -4.8      -2.4         -4.880004    -5.6
    @{yaw} =        Create List      -1.570796   -1.570796  -3.1415927  -3.1415927  0         -0.615480    0            0
    @{pitch} =      Create List      0           0          0           0           0         1.570796     0            0
    @{roll} =       Create List      0           0          -1.570796   1.570796    0         -0.615480    0            0
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${pt}    IN    @{ports}
        ${it}       Get From List      ${index}    ${i_step}
        ${tt}       Get From List      ${type}       ${i_step}
        ${parts}    Evaluate     $current.get("parts",{})
        ${port}     Evaluate     $parts.get("${pt}",{})
        ${part}     Evaluate     $port.get("${tt}",{})[${it}]
        ${pose}     Evaluate     $part.get("pose")
        ${typ}      Evaluate     $part.get("type")
        ${xt}       Get From List      ${x}          ${i_step}
        ${yt}       Get From List      ${y}          ${i_step}
        ${zt}       Get From List      ${z}          ${i_step}
        ${dyt}      Get From List      ${yaw}        ${i_step}
        ${dpt}      Get From List      ${pitch}      ${i_step}
        ${drt}      Get From List      ${roll}       ${i_step}
        Should Be Equal     ${tt}   ${typ}
        Should Be Equal As Numbers With Precision    ${xt}   ${pose.translation().x}    0.1
        Should Be Equal As Numbers With Precision    ${yt}   ${pose.translation().y}    0.1
        Should Be Equal As Numbers With Precision    ${zt}   ${pose.translation().z}    0.1
        Should Be Equal As Angles With Precision     ${dyt}  ${pose.rotation().z}       0.1    3.1415927
        Should Be Equal As Angles With Precision     ${dpt}  ${pose.rotation().y}       0.1    3.1415927
        Should Be Equal As Angles With Precision     ${drt}  ${pose.rotation().x}       0.1    3.1415927
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.2 Ensure Errors Are Handled Correctly
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_tank_pair
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${dynamics}     Create Dynamics  ${model}    0    0    0
    ${generator}    Use Object Method     ${dynamics}    start                 True   -1    E     D     0    100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    start_at_power        True   -1    E     D     0    100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    start_tank            True   -1    E     D     100    100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    start_tank_at_power   True   -1    E     D     0    100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    stop                  True   -1    E     D
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    move                  True   -1    E     D     5    0    100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    move_tank             True   -1    E     D     5    100   100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    start                 True   -1    D     F     0    100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    start_at_power        True   -1    D     F     0    100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    start_tank            True   -1    D     F     100    100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    start_tank_at_power   True   -1    D     F     0    100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    stop                  True   -1    D     F
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    move                  True   -1    D     F     5    0    100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}
    ${generator}    Use Object Method     ${dynamics}    move_tank             True   -1    D     F     5    100   100
    Run Keyword And Expect Error    RuntimeError: The motors could not be paired     Next Generator    ${generator}

5.3 Ensure Start Pair Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_pair
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
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
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method     ${dynamics}    start    True   -1        ${left}    ${right}  ${steering}  ${speed}
        ${shall_continue}     Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    200
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        END
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]          ${i_step}
        ${yt}       Get From List      ${tests}[y]          ${i_step}
        ${dt}       Get From List      ${tests}[direction]  ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]  ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]  ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.01
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    0.01
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    0.01
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.4 Ensure Start At Power Pair Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_pair
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]     ${i_step}
        ${east}        Get From List      ${tests}[east]      ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]       ${i_step}
        ${left}        Get From List      ${tests}[left]      ${i_step}
        ${right}       Get From List      ${tests}[right]     ${i_step}
        ${steering}    Get From List      ${tests}[steering]  ${i_step}
        ${power}       Get From List      ${tests}[speed]     ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method     ${dynamics}    start_at_power    True   -1    ${left}    ${right}  ${steering}  ${power}
        ${shall_continue}     Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    200
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        END
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]           ${i_step}
        ${yt}       Get From List      ${tests}[y]           ${i_step}
        ${dt}       Get From List      ${tests}[direction]   ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.01
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    0.01
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    0.01
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.5 Ensure Start Tank Pair Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_tank_pair
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${left}        Get From List      ${tests}[left]            ${i_step}
        ${right}       Get From List      ${tests}[right]           ${i_step}
        ${lspeed}      Get From List      ${tests}[left-command]    ${i_step}
        ${rspeed}      Get From List      ${tests}[right-command]   ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method     ${dynamics}    start_tank    True   -1    ${left}    ${right}  ${lspeed}  ${rspeed}
        ${shall_continue}     Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    200
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        END
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]           ${i_step}
        ${yt}       Get From List      ${tests}[y]           ${i_step}
        ${dt}       Get From List      ${tests}[direction]   ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.01
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    0.01
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    0.01
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.6 Ensure Start Tank At Power Pair Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_tank_pair
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${left}        Get From List      ${tests}[left]            ${i_step}
        ${right}       Get From List      ${tests}[right]           ${i_step}
        ${lspeed}      Get From List      ${tests}[left-command]    ${i_step}
        ${rspeed}      Get From List      ${tests}[right-command]   ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method     ${dynamics}    start_tank_at_power    True   -1    ${left}    ${right}  ${lspeed}  ${rspeed}
        ${shall_continue}     Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    200
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        END
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]           ${i_step}
        ${yt}       Get From List      ${tests}[y]           ${i_step}
        ${dt}       Get From List      ${tests}[direction]   ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.01
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    0.01
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    0.01
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.7 Ensure Move Pair Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    move_pair
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${left}        Get From List      ${tests}[left]            ${i_step}
        ${right}       Get From List      ${tests}[right]           ${i_step}
        ${steering}    Get From List      ${tests}[steering]        ${i_step}
        ${speed}       Get From List      ${tests}[speed]           ${i_step}
        ${amount}      Get From List      ${tests}[amount]          ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method     ${dynamics}    move    True   -1   ${left}    ${right}     ${amount}    ${steering}    ${speed}
        ${shall_continue}    Next Generator     ${generator}
        Should Be True       ${shall_continue}
        FOR  ${index}    IN RANGE    199
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
            ${shall_continue}    Next Generator     ${generator}
            Should Be True    ${shall_continue}
        END
        Use Object Method     ${dynamics}    extrapolate   False   -1   ${duration}
        ${shall_continue}    Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]           ${i_step}
        ${yt}       Get From List      ${tests}[y]           ${i_step}
        ${dt}       Get From List      ${tests}[direction]   ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.1
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.1
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    5
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    5
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.8 Ensure Move Tank Pair Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    move_tank_pair
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${left}        Get From List      ${tests}[left]            ${i_step}
        ${right}       Get From List      ${tests}[right]           ${i_step}
        ${lspeed}      Get From List      ${tests}[left-command]    ${i_step}
        ${rspeed}      Get From List      ${tests}[right-command]   ${i_step}
        ${amount}      Get From List      ${tests}[amount]          ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method     ${dynamics}    move_tank    True   -1   ${left}    ${right}     ${amount}    ${lspeed}    ${rspeed}
        ${shall_continue}     Next Generator     ${generator}
        Should Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    199
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
            ${shall_continue}    Next Generator     ${generator}
            Should Be True    ${shall_continue}
        END
        Use Object Method     ${dynamics}    extrapolate   False   -1   ${duration}
        ${shall_continue}    Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]           ${i_step}
        ${yt}       Get From List      ${tests}[y]           ${i_step}
        ${dt}       Get From List      ${tests}[direction]   ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]   ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]   ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.1
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.1
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    5
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    5
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.9 Ensure Stop Pair Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_tank_pair
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${left}        Get From List      ${tests}[left]            ${i_step}
        ${right}       Get From List      ${tests}[right]           ${i_step}
        ${lspeed}      Get From List      ${tests}[left-command]    ${i_step}
        ${rspeed}      Get From List      ${tests}[right-command]   ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method     ${dynamics}    start_tank    True   -1    ${left}    ${right}  ${lspeed}  ${rspeed}
        ${shall_continue}     Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    10
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        END
        ${generator}   Use Object Method     ${dynamics}    stop    True   -1    ${left}    ${right}
        ${shall_continue}     Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        ${initial}   Use Object Method  ${dynamics}    current    True
        ${position} =  Evaluate    ${initial}[parts][E][Motor][0][degrees] * ${initial}[parts][E][Motor][0][degrees] + ${initial}[parts][F][Motor][0][degrees] * ${initial}[parts][F][Motor][0][degrees] + ${initial}[parts][D][Motor][0][degrees] * ${initial}[parts][D][Motor][0][degrees]
        Should Not Be Equal As Numbers      ${position}         0
        FOR  ${index}    IN RANGE    100
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.01
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        END
        ${current}   Use Object Method  ${dynamics}    current    True
        Should Be Equal As Numbers With Precision     ${current}[x]                            ${initial}[x]                            0.01
        Should Be Equal As Numbers With Precision     ${current}[y]                            ${initial}[y]                            0.01
        Should Be Equal As Angles With Precision      ${current}[yaw]                          ${initial}[yaw]                          0.01
        Should Be Equal As Angles With Precision      ${current}[pitch]                        ${initial}[pitch]                        0.01
        Should Be Equal As Angles With Precision      ${current}[roll]                         ${initial}[roll]                         0.01
        Should Be Equal As Numbers With Precision     ${current}[parts][E][Motor][0][degrees]  ${initial}[parts][E][Motor][0][degrees]  0.01
        Should Be Equal As Numbers With Precision     ${current}[parts][F][Motor][0][degrees]  ${initial}[parts][F][Motor][0][degrees]  0.01
        Should Be Equal As Numbers With Precision     ${current}[parts][D][Motor][0][degrees]  ${initial}[parts][D][Motor][0][degrees]  0.01
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.10 Ensure Run To Position Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_to_position
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${port}        Get From List      ${tests}[port]            ${i_step}
        ${direction}   Get From List      ${tests}[dir]             ${i_step}
        ${speed}       Get From List      ${tests}[speed]           ${i_step}
        ${degrees}     Get From List      ${tests}[degrees]         ${i_step}
        ${delta}     Get From List        ${tests}[delta]           ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method  ${dynamics}    run_for_degrees   True    -1    ${port}    50         1021
        ${shall_continue}     Next Generator     ${generator}
        ${time}        Evaluate     0 + 0
        ${times} =  Convert To String    ${time}
        WHILE    ${shall_continue}  limit=1300
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${times}
            ${shall_continue}     Next Generator     ${generator}
            ${time}        Evaluate     ${time} + 0.005
            ${times} =  Convert To String    ${time}
        END
        ${status}   Use Object Method  ${dynamics}    current    True
        ${generator}   Use Object Method    ${dynamics}    run_to_position   True    -1    ${port}    ${speed}    ${degrees}    ${direction}
        ${shall_continue}     Next Generator     ${generator}
        ${steps}       Evaluate     ${duration} / ${delta} * ( ${delta} - ${status}[parts][${port}][Motor][0][degrees] + 1021 ) / 0.005 - 1
        Should Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    ${steps}
            ${delta} =  Evaluate    ${time} + ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
            ${shall_continue}    Next Generator     ${generator}
            Should Be True    ${shall_continue}
        END
        ${delta} =  Evaluate    ${time} + ${duration}
        ${delta} =  Convert To String    ${delta}
        Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        ${shall_continue}    Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]               ${i_step}
        ${yt}       Get From List      ${tests}[y]               ${i_step}
        ${dt}       Get From List      ${tests}[direction]       ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
        ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.1
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.1
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    5
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  ${ot}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    5
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.11 Ensure Run For Degrees Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_for_degrees
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${port}        Get From List      ${tests}[port]            ${i_step}
        ${speed}       Get From List      ${tests}[speed]           ${i_step}
        ${degrees}     Get From List      ${tests}[degrees]         ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}      Use Object Method    ${dynamics}    run_for_degrees   True    -1    ${port}    ${speed}    ${degrees}
        ${shall_continue}     Next Generator     ${generator}
        Should Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    199
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
            ${shall_continue}    Next Generator     ${generator}
            Should Be True    ${shall_continue}
        END
        Use Object Method     ${dynamics}    extrapolate   False   -1   ${duration}
        ${shall_continue}    Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]               ${i_step}
        ${yt}       Get From List      ${tests}[y]               ${i_step}
        ${dt}       Get From List      ${tests}[direction]       ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
        ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.1
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.1
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    5
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  ${ot}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    5
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.12 Ensure Run For Rotations Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_for_degrees
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${port}        Get From List      ${tests}[port]            ${i_step}
        ${speed}       Get From List      ${tests}[speed]           ${i_step}
        ${degrees}     Get From List      ${tests}[degrees]         ${i_step}
        ${rotations}   Evaluate     ${degrees} * 1.0/360
        ${rotations}   Convert To String    ${rotations}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}      Use Object Method    ${dynamics}    run_for_rotations   True    -1    ${port}    ${speed}    ${rotations}
        ${shall_continue}     Next Generator     ${generator}
        Should Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    199
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
            ${shall_continue}     Next Generator     ${generator}
            Should Be True    ${shall_continue}
        END
        Use Object Method     ${dynamics}    extrapolate   False   -1   ${duration}
        ${shall_continue}    Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]               ${i_step}
        ${yt}       Get From List      ${tests}[y]               ${i_step}
        ${dt}       Get From List      ${tests}[direction]       ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
        ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.1
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.1
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    5
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  ${ot}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    5
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.13 Ensure Run To Degrees Counted Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_to_degrees_counted
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${port}        Get From List      ${tests}[port]            ${i_step}
        ${speed}       Get From List      ${tests}[speed]           ${i_step}
        ${degrees}     Get From List      ${tests}[degrees]         ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}      Use Object Method    ${dynamics}    run_to_degrees_counted   True    -1    ${port}    ${speed}    ${degrees}
        ${shall_continue}     Next Generator     ${generator}
        Should Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    199
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
            ${shall_continue}     Next Generator     ${generator}
            Should Be True    ${shall_continue}
        END
        Use Object Method     ${dynamics}    extrapolate   False   -1   ${duration}
        ${shall_continue}    Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]               ${i_step}
        ${yt}       Get From List      ${tests}[y]               ${i_step}
        ${dt}       Get From List      ${tests}[direction]       ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
        ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.1
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.1
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    5
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  ${ot}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    5
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.14 Ensure Run For Seconds Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    run_for_seconds
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    &{timer_conf}   Create Dictionary     mode=controlled    period=0.005
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${port}        Get From List      ${tests}[port]            ${i_step}
        ${speed}       Get From List      ${tests}[speed]           ${i_step}
        ${dynamics}    Create Dynamics    ${model}    ${north}  ${east}    ${yaw}
        Use Object Method  ${dynamics.s_shared_timer}    configure    False    -1    ${timer_conf}
        ${generator}      Use Object Method    ${dynamics}    run_for_seconds   True    -1    ${port}    ${speed}    ${duration}
        ${shall_continue}     Next Generator     ${generator}
        Should Be True    ${shall_continue}
        ${steps}        Evaluate     ${duration} / 0.005 - 1
        FOR  ${index}    IN RANGE    ${steps}
            Use Object Method     ${dynamics.s_shared_timer}    step    False
            ${date}    Use Object Method     ${dynamics.s_shared_timer}    time    True    -1
            ${date} =  Convert To String     ${date}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${date}
            ${shall_continue}    Next Generator     ${generator}
            Should Be True    ${shall_continue}
        END
        Use Object Method     ${dynamics.s_shared_timer}    step    False
        Use Object Method     ${dynamics}    extrapolate   False   -1   ${duration}
        ${shall_continue}    Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]               ${i_step}
        ${yt}       Get From List      ${tests}[y]               ${i_step}
        ${dt}       Get From List      ${tests}[direction]       ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]       ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]       ${i_step}
        ${ot}       Get From List      ${tests}[D-degrees]       ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.1
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.1
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    5
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  ${ot}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    5
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    5
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.15 Ensure Start Single Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_single
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]     ${i_step}
        ${east}        Get From List      ${tests}[east]      ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]       ${i_step}
        ${port}        Get From List      ${tests}[port]      ${i_step}
        ${speed}       Get From List      ${tests}[speed]     ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method     ${dynamics}    start    True   -1        ${port}    ${speed}
        ${shall_continue}     Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    200
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        END
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]          ${i_step}
        ${yt}       Get From List      ${tests}[y]          ${i_step}
        ${dt}       Get From List      ${tests}[direction]  ${i_step}
        ${ot}       Get From List      ${tests}[D-degrees]  ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]  ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]  ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.01
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    0.01
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  ${ot}    0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    0.01
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.16 Ensure Start At Power Single Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_single
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]     ${i_step}
        ${east}        Get From List      ${tests}[east]      ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]       ${i_step}
        ${port}        Get From List      ${tests}[port]      ${i_step}
        ${speed}       Get From List      ${tests}[speed]     ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method     ${dynamics}    start_at_power    True   -1        ${port}    ${speed}
        ${shall_continue}     Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    200
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        END
        ${status}   Use Object Method  ${dynamics}    current    True
        ${xt}       Get From List      ${tests}[x]          ${i_step}
        ${yt}       Get From List      ${tests}[y]          ${i_step}
        ${dt}       Get From List      ${tests}[direction]  ${i_step}
        ${ot}       Get From List      ${tests}[D-degrees]  ${i_step}
        ${lt}       Get From List      ${tests}[E-degrees]  ${i_step}
        ${rt}       Get From List      ${tests}[F-degrees]  ${i_step}
        Should Be Equal As Numbers With Precision     ${status}[x]                            ${xt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[y]                            ${yt}    0.01
        Should Be Equal As Angles With Precision      ${status}[yaw]                          ${dt}    0.01
        Should Be Equal As Angles With Precision      ${status}[pitch]                        0        0.01
        Should Be Equal As Angles With Precision      ${status}[roll]                         0        0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][D][Motor][0][degrees]  ${ot}    0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][E][Motor][0][degrees]  ${lt}    0.01
        Should Be Equal As Numbers With Precision     ${status}[parts][F][Motor][0][degrees]  ${rt}    0.01
        ${i_step} =     Set Variable   ${i_step + 1}
    END

5.17 Ensure Stop Single Moves Robot According To Its Dynamics Data
    [Tags]          Dynamics
    ${tests}        Read Test Case Parameters    ${TEST_FILE}    start_single
    ${model}        Create model     ${ROBOT_JSON_CONF_FILE}
    ${i_step} =     Set Variable     0
    ${i_step} =     Convert To Integer  ${i_step}
    FOR    ${duration}    IN    @{tests}[duration]
        ${north}       Get From List      ${tests}[north]           ${i_step}
        ${east}        Get From List      ${tests}[east]            ${i_step}
        ${yaw}         Get From List      ${tests}[yaw]             ${i_step}
        ${port}        Get From List      ${tests}[port]            ${i_step}
        ${speed}       Get From List      ${tests}[speed]           ${i_step}
        ${dynamics}    Create Dynamics  ${model}    ${north}  ${east}    ${yaw}
        ${generator}   Use Object Method     ${dynamics}    start    True    -1    ${port}    ${speed}
        ${shall_continue}     Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        FOR  ${index}    IN RANGE    10
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        END
        ${generator}   Use Object Method     ${dynamics}    stop    True   -1    ${port}
        ${shall_continue}     Next Generator     ${generator}
        Should Not Be True    ${shall_continue}
        ${initial}   Use Object Method  ${dynamics}    current    True
        ${position} =  Evaluate    ${initial}[parts][E][Motor][0][degrees] * ${initial}[parts][E][Motor][0][degrees] + ${initial}[parts][F][Motor][0][degrees] * ${initial}[parts][F][Motor][0][degrees] + ${initial}[parts][D][Motor][0][degrees] * ${initial}[parts][D][Motor][0][degrees]
        Should Not Be Equal As Numbers      ${position}         0
        FOR  ${index}    IN RANGE    200
            ${delta} =  Evaluate    ${duration} * ( ${index} + 1 ) * 0.005
            ${delta} =  Convert To String    ${delta}
            Use Object Method     ${dynamics}    extrapolate   False   -1   ${delta}
        END
        ${current}   Use Object Method  ${dynamics}    current    True
        Should Be Equal As Numbers With Precision     ${current}[x]                            ${initial}[x]                            0.01
        Should Be Equal As Numbers With Precision     ${current}[y]                            ${initial}[y]                            0.01
        Should Be Equal As Angles With Precision      ${current}[yaw]                          ${initial}[yaw]                          0.01
        Should Be Equal As Angles With Precision      ${current}[pitch]                        ${initial}[pitch]                        0.01
        Should Be Equal As Angles With Precision      ${current}[roll]                         ${initial}[roll]                         0.01
        Should Be Equal As Numbers With Precision     ${current}[parts][E][Motor][0][degrees]  ${initial}[parts][E][Motor][0][degrees]  0.01
        Should Be Equal As Numbers With Precision     ${current}[parts][F][Motor][0][degrees]  ${initial}[parts][F][Motor][0][degrees]  0.01
        Should Be Equal As Numbers With Precision     ${current}[parts][D][Motor][0][degrees]  ${initial}[parts][D][Motor][0][degrees]  0.01
        ${i_step} =     Set Variable   ${i_step + 1}
    END
