# standart library imports
import json
import os
import sys

def dir_scan(dir_name):
    """
    Perform recursive scan of directories for files
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

def init_config():

    resources = dir_scan("resources")
    gui = dir_scan("gui")

    config = {
        "resources": resources,
        "gui": gui
    }
    with open("config.json", 'w') as file:
        json.dump(config, file, indent=4)

# Load config files
if __name__ == '__main__':
    init_config()
