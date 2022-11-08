import config
import os
import sys


# Autonomous driving related output in case of emergency
def selfDriving():
    print("--> The car moves to the shoulder and stops with the flash on the hazard lights.\n"
          "\tFinished simulation\n")
    input("Enter any key to quit: ")
    quitMsg()


# When quitting the selected simulation
def quitMsg():
    print("--> Quitting Heart Rate Simulator...")


# When the simulation shut down / exit
def exitMsg():
    print("--> Finished simulator\n")


# Main routine start here: Heart Rate Simulator
def mainProgress():
    # First page, this is a function to automatically set the environment before starting
    initalPage = True
    while initalPage:
        print("\nHeart rate situation with autonomous vehicle"
              "\n1) Start simulation"
              "\n2) Config: Setup configure file to connect IoT Central"
              "\n3) Config: System environment setting (JUST ONE TIME)"
              "\n4) Config: Install dependency library"
              "\n0) Quit the simulator")
        answer = input("Select command: ")
        if answer == "1":
            initalPage = False
        elif answer == "2":
            config.setConfig()
            sys.exit()
        elif answer == "3":
            print("\nWARNING\nTHIS IS JUST ONE TIME SETUP")
            addshrc = input("Are you sure add under .bashrc file? (Y/n): ")
            if addshrc == "y" or addshrc == "Y":
                config.addbashrc()
                sys.exit()
            elif addshrc == "n" or addshrc == "N":
                print("--> Stopped to add")
            else:
                print("--> Please choose Y(yes) or n(no)\n"
                      "\tPlease Retry again\n")
        elif answer == "4":
            config.installRequirement()
        elif answer == "0" or answer == "exit" or answer == "q" or answer == "Q":
            exitMsg()
            sys.exit()
        else:
            print("--> please choose number 0-4")

    # situation are printed
    # Please check with the connected IoT Central device
    simulationPage = True
    ememsg = "--> Automatically Emergency call and send your situation now\n"
    print("\n\n\n-----Heart Rate Simulator-----")
    while simulationPage:
        print("\nChoose situation\n"
              "1) Normal heart rate (H.R.: 60-100)\n"
              "2) Low heart rate (H.R.: 40-59)\n"
              "3) Too low heart rate (H.R.: 1-39)\n"
              "4) Heart arrest (H.R.: 0)\n"
              "0) Quit the simulator")
        answer = input("Select command: ")

        if answer == "1":
            print("--> Start normal heart rate\n")
            os.system("python3 heartnormal.py")

        elif answer == "2":
            print("--> Start low heart rate\n")
            os.system("python3 heartlow.py")
            emer = input("--> Really call emergency assistance? (Y/n) ")
            if emer == "y" or emer == "Y" or emer == "yes" or emer == "Yes" or emer == "YES":
                print(ememsg)
                os.system("python3 locationhrlow.py")
                selfDriving()
            elif emer == "n" or emer == "N" or emer == "no" or emer == "No" or emer == "NO":
                print("--> Changed your heart rate normally\n")
                os.system("python3 heartnormal.py")
            else:
                quitMsg()

        elif answer == "3":
            print("--> Start too low heart rate\n")
            os.system("python3 hearttoolow.py")
            print(ememsg)
            os.system("python3 locationhrtoolow.py")
            selfDriving()

        elif answer == "4":
            print("--> Start heart arrest\n")
            os.system("python3 heartarrest.py")
            print(ememsg)
            os.system("python3 locationhrarrest.py")
            selfDriving()

        elif answer == "0" or answer == "exit" or answer == "q" or answer == "Q":
            exitMsg()
            simulationPage = False
        else:
            print("--> please choose number 0-4")


if __name__ == '__main__':
    mainProgress()
