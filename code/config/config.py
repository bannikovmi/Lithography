# standart library imports
import json
import os
import sys

resources = {}

def dir_scan(dir_name):
    """
    Perform tecursive scan of directories for files
    with .json extension and add them to dictionary.
    """

    ret = {}

    for name in os.listdir(dir_name):

        new_path = os.path.join(dir_name, name)
        if os.path.isdir(new_path):
            ret[name] = dir_scan(new_path)
        else:
            with open(new_path, "r") as file:
                ret[name.split('.')[0]] = json.load(file)

    return ret

resources = dir_scan("resources")

config = {
    "resources": resources
}
with open("config.json", 'w') as file:
    json.dump(config, file, indent=4)
