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
Library         ../keywords/scenario.py
Library         Collections

*** Variables ***
${SCENARIO_FILE}            ${data}/rort.json
${ROBOT_JSON_CONF_FILE}     ${data}/robot.json

*** Test Cases ***
13.1 Ensure Scenario Registers Components
    [Tags]           Robot
    ${scenario}        Create Scenario       ${SCENARIO_FILE}    ${ROBOT_JSON_CONF_FILE}    time

    ${button1}       Create Object    Button    left
    ${button2}       Create Object    Button    right
    Run Keyword And Expect Error	ValueError: Button already created on side left    Create Object    Button    left
    Run Keyword And Expect Error	ValueError: Unknown side for button    Create Object    Button    whatever

    ${motor1}        Create Object    Motor    E
    ${motor2}        Create Object    Motor    F
    Run Keyword And Expect Error	ValueError: Motor already created on port E    Create Object    Motor    E
    Run Keyword And Expect Error	ValueError: Port A does not host a motor   Create Object    Motor    A
    Run Keyword And Expect Error	ValueError: Port whatever not used on robot    Create Object    Motor    whatever

    ${motorpair}     Create Object     MotorPair     E     F
    Run Keyword And Expect Error	ValueError: Motorpair already created   Create Object    MotorPair    E    F
    Run Keyword And Expect Error	ValueError: Motor not created on port A  Create Object    MotorPair    A    F
    Run Keyword And Expect Error	ValueError: Motor not created on port whatever  Create Object    MotorPair    whatever    F

    ${color1}        Create Object    ColorSensor    A
    Run Keyword And Expect Error	ValueError: Color sensor already created on port A    Create Object    ColorSensor    A
    Run Keyword And Expect Error	ValueError: Port D does not host a color sensor   Create Object    ColorSensor    D
    Run Keyword And Expect Error	ValueError: Port whatever not used on robot    Create Object    ColorSensor    whatever

    ${distance1}     Create Object    DistanceSensor    C
    Run Keyword And Expect Error	ValueError: Distance sensor already created on port C    Create Object    DistanceSensor    C
    Run Keyword And Expect Error	ValueError: Port D does not host a distance sensor   Create Object    DistanceSensor    D
    Run Keyword And Expect Error	ValueError: Port whatever not used on robot    Create Object    DistanceSensor    whatever

    ${force1}        Create Object    ForceSensor    B
    Run Keyword And Expect Error	ValueError: Force sensor already created on port B   Create Object    ForceSensor    B
    Run Keyword And Expect Error	ValueError: Port D does not host a force sensor    Create Object    ForceSensor    D
    Run Keyword And Expect Error	ValueError: Port whatever not used on robot    Create Object    ForceSensor    whatever

    ${lightmatrix}   Create Object    LightMatrix
    Run Keyword And Expect Error	ValueError: Light matrix already created   Create Object    LightMatrix

    ${motionsensor}  Create Object    MotionSensor
    Run Keyword And Expect Error	ValueError: Motion sensor already created   Create Object    MotionSensor

    ${speaker}       Create Object    Speaker
    Run Keyword And Expect Error	ValueError: Speaker already created   Create Object    Speaker

    ${statuslight}   Create Object    StatusLight
    Run Keyword And Expect Error	ValueError: Status light already created   Create Object    StatusLight

    [Teardown]      Reset Scenario  ${scenario}


