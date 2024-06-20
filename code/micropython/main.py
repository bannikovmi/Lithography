# jeneral imports
import sys

# local imports
from resource.command import Command

# import resource classes
from ESP.ESP import ESP
from tmc.drive import Drive
from aht.AHT import AHT
from misc.LED import LED
from misc.switch import Switch

# Initialize ESP and resources
esp = ESP(config_file="config//config.json")

resources = {
    "ESP": esp,
    # "PMP": Switch(esp=esp, name="PMP"),
    # "FAN": Switch(esp=esp, name="FAN"),
    "AHT": AHT(esp=esp, name="AHT"),
    "BLD": LED(esp=esp, name="BLD"),
    "RLD": LED(esp=esp, name="RLD"),
    "DRX": Drive(esp=esp, name="DRX"),
    "DRY": Drive(esp=esp, name="DRY"),
    "DRZ": Drive(esp=esp, name="DRZ"),
    "DRL": Drive(esp=esp, name="DRL"),
}

while True:
        
    command = Command(input())
    result = resources[command.resource_name].exec_command(command.name, *command.args)
