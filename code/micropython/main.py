# 
import sys, select, time, json

# local imports
from lib.command import Command

# import resources classes
from lib.esp import ESP
from lib.drive import Drive
from lib.DHT import DHT
from lib.LED import LED
from lib.switch import Switch

# Initialize ESP and resources
esp = ESP(config_file="config.json")

resources = {
    "ESP": esp,
    "PMP": Switch(esp=esp, name="PMP"),
    "FAN": Switch(esp=esp, name="FAN"),
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
