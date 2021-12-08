** Settings ***
Library        pyats.robot.pyATSRobot
Library        genie.libs.robot.GenieRobot        

** Variables **
${tbr}       testbed/routers.yml

*** Test Cases ***

Connect
    use genie testbed "${tbr}"
    connect to devices "R1"
    
Is BGP running properly?
    Profile the system for "bgp" on devices "R1" as "./profiletest"
