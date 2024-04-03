# 
import sys, select, time, json
# 
# local imports
from lib.command import Command

from machine import Pin

# import resources classes
from lib.esp import ESP
from lib.drive import Drive
from lib.DHT import DHT

# Initialize ESP and resources and save them into dictionary
esp = ESP(config_file="config.json")

resources = {
    "ESP": esp,
    "DHT": DHT(esp=esp, bus_id = 13),
    "DRX": Drive(esp=esp, name="DRX", en_id=15, step_id=2, dir_id=4,
        max_id=16, min_id=17),
    # "DRY": Drive(esp=esp, name="DRY", en_id = 5, step_id = 6, dir_id = 7,
    #     max_id = 8, min_id = 9),
    # "DRZ": Drive(esp=esp, name="DRZ", en_id = 10, step_id = 11, dir_id = 12,
    #     max_id = 13, min_id = 14),
}

while True:
        
    command = Command(input())
    result = resources[command.resource_name].exec_command(command.name, *command.args)
