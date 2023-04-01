 -------------------------------------------------------
# Copyright (c) [2022] Nadege LEMPERIERE
# All rights reserved
# -------------------------------------------------------
# Robotframework test suite to test part positioning
# -------------------------------------------------------
# Nadège LEMPERIERE, @04 november 2022
# Latest revision: 04 november 2022
# -------------------------------------------------------

*** Settings ***
Documentation   A test case to check part positioning
Library         ../keywords/objects.py
Library         ../keywords/scenario.py
Library         ../keywords/dynamics.py
Library         Collections

*** Variables ***
${MAT_FILE}     mat.png
${MAT_PATH}     ${data}

*** Test Cases ***

12.1 Ensure Part Relative Position Is Correct
    [Tags]    Part
    @{north} =  Create List    12         12         0
    @{east} =   Create List    34         34         0
    @{down} =   Create List    56         56         0
    @{roll} =   Create List    78         18         78
    @{pitch} =  Create List    11         11         11
    @{yaw} =    Create List    23         23         23
    @{x1} =     Create List    0          0          -12
    @{y1} =     Create List    0          0          -34
    @{z1} =     Create List    0          0          -56
    @{rx1} =    Create List    0          -1.047198  0
    @{ry1} =    Create List    0          0          0
    @{rz1} =    Create List    0          0          0
    @{x2} =     Create List    12         12         -25.370102
    @{y2} =     Create List    34         34         69.964619
    @{z2} =     Create List    56         56         14.214576
    @{rx2} =    Create List    1.361357   0.314159   1.36135
    @{ry2} =    Create List    0.191986   0.191986   0.191986
    @{rz2} =    Create List    0.401426   0.401426   0.401426
    ${i_step} =         Set Variable   0
    ${i_step} =         Convert To Integer  ${i_step}
    FOR    ${yt}    IN    @{yaw}
        ${pt}       Get From List        ${pitch}      ${i_step}
        ${rt}       Get From List        ${roll}       ${i_step}
        ${nt}       Get From List        ${north}      ${i_step}
        ${et}       Get From List        ${east}       ${i_step}
        ${dt}       Get From List        ${down}       ${i_step}
        ${x1t}      Get From List        ${x1}         ${i_step}
        ${y1t}      Get From List        ${y1}         ${i_step}
        ${z1t}      Get From List        ${z1}         ${i_step}
        ${rx1t}     Get From List        ${rx1}        ${i_step}
        ${ry1t}     Get From List        ${ry1}        ${i_step}
        ${rz1t}     Get From List        ${rz1}        ${i_step}
        ${x2t}      Get From List        ${x2}         ${i_step}
        ${y2t}      Get From List        ${y2}         ${i_step}
        ${z2t}      Get From List        ${z2}         ${i_step}
        ${rx2t}     Get From List        ${rx2}        ${i_step}
        ${ry2t}     Get From List        ${ry2}        ${i_step}
        ${rz2t}     Get From List        ${rz2}        ${i_step}
        ${part}         Create Part    ColorSensor    ${nt}    ${et}    ${dt}    ${rt}    ${pt}    ${yt}
        ${pose}         CreatePose     12   34    56    78    11    23
        Use Object Method    ${part}    derive_relative    False    -1   ${pose}
        Use Object Method    ${part}    derive_pose        False    -1   ${pose}
        Should Be Equal As Numbers With Precision    ${part.relative.translation().X()}   ${x1t}          0.0001
        Should Be Equal As Numbers With Precision    ${part.relative.translation().Y()}   ${y1t}          0.0001
        Should Be Equal As Numbers With Precision    ${part.relative.translation().Z()}   ${z1t}          0.0001
        Should Be Equal As Numbers With Precision    ${part.relative.rotation().X()}      ${rx1t}         0.0001
        Should Be Equal As Numbers With Precision    ${part.relative.rotation().Y()}      ${ry1t}         0.0001
        Should Be Equal As Numbers With Precision    ${part.relative.rotation().Z()}      ${rz1t}         0.0001
        Should Be Equal As Numbers With Precision    ${part.pose.translation().X()}       ${x2t}          0.0001
        Should Be Equal As Numbers With Precision    ${part.pose.translation().Y()}       ${y2t}          0.0001
        Should Be Equal As Numbers With Precision    ${part.pose.translation().Z()}       ${z2t}          0.0001
        Should Be Equal As Numbers With Precision    ${part.pose.rotation().X()}          ${rx2t}         0.0001
        Should Be Equal As Numbers With Precision    ${part.pose.rotation().Y()}          ${ry2t}         0.0001
        Should Be Equal As Numbers With Precision    ${part.pose.rotation().Z()}          ${rz2t}         0.0001
        ${i_step} =     Set Variable   ${i_step + 1}
    END

12.2 Ensure Color Sensor Direction Is Correct
    [Tags]     Part
    ${mat}        Create Mat     ${MAT_FILE}    ${MAT_PATH}
    @{yaw} =      Create List    0     0     45    20    0     0     45    20
    @{pitch} =    Create List    90    45    45    20    90    45    45    20
    @{north} =    Create List    40    40    40    40    50    50    50    50
    @{east} =     Create List    40    40    40    40    50    50    50    50
    @{red} =      Create List    188   178   224   191   166   117   105   0
    @{green} =    Create List    178   203   206   193   166   156   162   0
    @{blue} =     Create List    165   117   114   212   164   126   111   0
    ${i_step} =         Set Variable   0
    ${i_step} =         Convert To Integer  ${i_step}
    FOR    ${yt}    IN    @{yaw}
        ${pt}       Get From List        ${pitch}            ${i_step}
        ${nt}       Get From List        ${north}            ${i_step}
        ${et}       Get From List        ${east}             ${i_step}
        ${part}     Create Color Sensor  ${nt}    ${et}    -20    0    ${pt}    ${yt}
        Use Object Method    ${part}     read_color     False    -1   ${mat}
        ${status}   Use Object Method    ${part}    export   True    -1
        ${rt}       Get From List        ${red}              ${i_step}
        ${gt}       Get From List        ${green}            ${i_step}
        ${bt}       Get From List        ${blue}             ${i_step}
        Should Be Equal As Numbers With Precision    ${rt}    ${status}[red]     1
        Should Be Equal As Numbers With Precision    ${gt}    ${status}[green]   1
        Should Be Equal As Numbers With Precision    ${bt}    ${status}[blue]    1
        ${i_step} =     Set Variable   ${i_step + 1}
    END