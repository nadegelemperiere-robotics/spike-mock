# -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test spike light matrix mock
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

*** Settings ***
Documentation   A test case to check light matrix mock functioning
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

8.1 Ensure Light Matrix Is Created With The Required Constants
    [Tags]  LightMatrix
    ${scenario}     Create Scenario     ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario  ${scenario}
    ${matrix}       Create Object    LightMatrix
    @{members} =    Create List      show_image    set_pixel    write     off
    Should Have Members    ${matrix}    ${members}
    [Teardown]      Reinitialize Scenario   ${scenario}

8.2 Test Light Matrix Image Display On Read Only Time Controlled Scenario
    [Tags]    LightMatrix
    ${scenario}     Create Scenario     ${ROTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario  ${scenario}
    ${matrix}       Create Object    LightMatrix
    Use Object Method  ${matrix}  show_image    False    -1    HEART
    Play Scenario During Steps      1
    ${heart}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${heart}    0
    Should Be Equal As Integers   ${p}        0
    ${p}            Get From List      ${heart}    1
    Should Be Equal As Integers   ${p}        100
    Use Object Method  ${matrix}  set_pixel   False    -1    0    0    50
    Play Scenario During Steps      1
    ${heart}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${heart}    0
    Should Be Equal As Integers   ${p}        50
    Use Object Method  ${matrix}  off
    Play Scenario During Steps      1
    ${empty}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${empty}    0
    Should Be Equal As Integers   ${p}        0
    ${p}            Get From List      ${empty}    1
    Should Be Equal As Integers   ${p}        0
    [Teardown]      Reinitialize Scenario   ${scenario}

8.3 Test Light Matrix Image Display On Read Only Real Time Scenario
    [Tags]    LightMatrix
    ${scenario}     Create Scenario     ${RORT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario  ${scenario}
    ${matrix}       Create Object    LightMatrix
    Use Object Method  ${matrix}  show_image    False    -1    HEART
    Sleep           0.1
    ${heart}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${heart}    0
    Should Be Equal As Integers   ${p}        0
    ${p}            Get From List      ${heart}    1
    Should Be Equal As Integers   ${p}        100
    Use Object Method  ${matrix}  set_pixel   False    -1    0    0    50
    Sleep           0.1
    ${heart}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${heart}    0
    Should Be Equal As Integers   ${p}        50
    Use Object Method  ${matrix}  off
    Sleep           0.1
    ${empty}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${empty}    0
    Should Be Equal As Integers   ${p}        0
    ${p}            Get From List      ${empty}    1
    Should Be Equal As Integers   ${p}        0
    [Teardown]      Reinitialize Scenario   ${scenario}

8.4 Test Light Matrix Image Display On Computed Time Controlled Scenario
    [Tags]    LightMatrix
    ${scenario}     Create Scenario     ${CPTC_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario  ${scenario}
    ${matrix}       Create Object    LightMatrix
    Use Object Method  ${matrix}  show_image    False    -1    HEART
    Play Scenario During Steps      1
    ${heart}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${heart}    0
    Should Be Equal As Integers   ${p}        0
    ${p}            Get From List      ${heart}    1
    Should Be Equal As Integers   ${p}        100
    Use Object Method  ${matrix}  set_pixel   False    -1    0    0    50
    Play Scenario During Steps      1
    ${heart}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${heart}    0
    Should Be Equal As Integers   ${p}        50
    Use Object Method  ${matrix}  off
    Play Scenario During Steps      1
    ${empty}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${empty}    0
    Should Be Equal As Integers   ${p}        0
    ${p}            Get From List      ${empty}    1
    Should Be Equal As Integers   ${p}        0
    [Teardown]      Reinitialize Scenario   ${scenario}

8.5 Test Light Matrix Image Display On Computed Real Time Scenario
    [Tags]    LightMatrix
    ${scenario}     Create Scenario     ${CPRT_JSON_CONF_FILE}    ${ROBOT_JSON_CONF_FILE}  time
    Start Scenario  ${scenario}
    ${matrix}       Create Object    LightMatrix
    Use Object Method  ${matrix}  show_image    False    -1    HEART
    Sleep           0.1
    ${heart}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${heart}    0
    Should Be Equal As Integers   ${p}        0
    ${p}            Get From List      ${heart}    1
    Should Be Equal As Integers   ${p}        100
    Use Object Method  ${matrix}  set_pixel   False    -1    0    0    50
    Sleep           0.1
    ${heart}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${heart}    0
    Should Be Equal As Integers   ${p}        50
    Use Object Method  ${matrix}  off
    Sleep           0.1
    ${empty}        Use Object Method  ${matrix}   c_get_matrix    True
    ${p}            Get From List      ${empty}    0
    Should Be Equal As Integers   ${p}        0
    ${p}            Get From List      ${empty}    1
    Should Be Equal As Integers   ${p}        0
    [Teardown]      Reinitialize Scenario   ${scenario}
