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
Documentation   A test case to check data loading functioning
Library         ../keywords/objects.py
Library         ../keywords/data.py
Library         Collections

*** Variables ***
${DATA_FILE}            ${data}/data.xlsx

*** Test Cases ***

3.1 Ensure Data Time Extrapolation Is Correct
    [Tags]    Data
    ${data}        Load Data            ${DATA_FILE}    motors
    @{dates} =     Create List    0    38.2        20           20.1         20.01        20.05       20.07
    @{degrees} =   Create List    0    497.431533  260.4353576  261.7375344  260.5655753  261.086446  261.3468813
    ${i_step} =    Set Variable    0
    ${i_step} =    Convert To Integer  ${i_step}
    FOR    ${date}    IN    @{dates}
        ${d}     Use Object Method    ${data}         extrapolate    True    -1    E_degrees    ${date}
        ${dt}    Get From List        ${degrees}      ${i_step}
        Should Be Equal As Numbers     ${dt}          ${d}
        ${i_step} =     Set Variable   ${i_step + 1}
    END