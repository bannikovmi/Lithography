# 
import sys, select, time
# 
# local imports
from lib.command import Command

# import resources classes
from lib.esp import ESP
from lib.drive import Drive
from lib.DHT import DHT

# Initialize resources and save them into dictionary
esp = ESP()
resources = {
    "ESP": esp,
    "DHT": DHT(esp=esp, bus_id = 13),
    "DRX": Drive(esp=esp, name="DRX", en_id = 15, step_id = 2, dir_id = 4,
        max_id = 16, min_id = 17),
}

while True:
        
    command = Command(input())
    result = resources[command.resource_name].exec_command(command.name, *command.args)
