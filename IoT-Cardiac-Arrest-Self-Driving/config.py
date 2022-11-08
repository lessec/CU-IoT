import os.path
import subprocess

userdir = os.path.expanduser("~")
bashrl = "\tPleas system quit and reload .bashrc\n\tPlease enter on terminal: source ~/.bashrc"


# Install python libray automatically
def installRequirement():
    subprocess.call('pip3 install -r requirements.txt', shell=True)
    print("--> Successfully installed!\n" + bashrl)


# Add config file on .bashrc (environment setting)
def addbashrc():
    bashrc = open(f"{userdir}/.bashrc", "a")
    bashrc.write("\n\n# IOT CENTRAL CONNECT (DPS) SYSENV\n"
                 "source ~/.iot-hr-config\n")
    bashrc.close()
    print("--> Successfully add!\n" + bashrl)


# Create or recreate config file (environment setting)
def setConfig():
    id_scope = input("Write ID scope: ")
    device_id = input("Write Device ID: ")
    primary_key = input("Write Primary key: ")
    conf_dps = open(f"{userdir}/.iot-hr-config", "w")
    conf_dps.write("export IOTHUB_DEVICE_SECURITY_TYPE=\'DPS\'\n")
    conf_dps.write(f"export IOTHUB_DEVICE_DPS_ID_SCOPE=\'{id_scope}\'\n")
    conf_dps.write(f"export IOTHUB_DEVICE_DPS_DEVICE_KEY=\'{primary_key}\'\n")
    conf_dps.write(f"export IOTHUB_DEVICE_DPS_DEVICE_ID=\'{device_id}\'\n")
    conf_dps.write(f"export IOTHUB_DEVICE_DPS_ENDPOINT=\'global.azure-devices-provisioning.net\'\n")
    conf_dps.close()
    print("--> Successfully setup configuration and ready to connect!\n" + bashrl)
