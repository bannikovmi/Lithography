import json

config = {
    "ESP": {
        "int_id": 23,
        "scl_id": 22,
        "sda_id": 21,
        "blink_id": 2,
    },
    "PMP": {
        "pin_id": 18,
        "btn_id": 34,
        "on_startup": False,
    },
    "FAN": {
        "pin_id": 19,
        "btn_id": 35,
        "on_startup": True,
    },
    "BLD": {
        "pin_id": 2,
        "freq": 1000,
        "duty": 5,
    },
    "RLD": {
        "pin_id": 15,
        "freq": 1000,
        "duty": 5,
    },
    "DRX": {
    	"uart_addr": 0,
        "en_id": 0,
        "step_id": 32,
        "dir_id": 33,
        "min_id": 4,
        "max_id": 5,
        "microstep": 1,
        "pos_dir": 1,
        "limit_on": 1,
    },
    "DRY": {
	    "uart_addr": 1,
        "en_id": 1,
        "step_id": 2,
        "dir_id": 26,
        "min_id": 6,
        "max_id": 7,
        "microstep": 1,
        "pos_dir": 1,
        "limit_on": 1,
    },
    "DRZ": {
    	"uart_addr": 2,
        "en_id": 2,
        "step_id": 14,
        "dir_id": 27,
        "min_id": 11,
        "max_id": 10,
        "microstep": 1,
        "pos_dir": 0,
        "limit_on": 1,
        "speed": 1000
    },
    "DRL": {
    	"uart_addr": 3,
        "en_id": 3,
        "step_id": 13,
        "dir_id": 12,
        "min_id": 13,
        "max_id": 12,
        "microstep": 1,
        "pos_dir": 1,
        "limit_on": 1,
    },
    "UART": {
        "id": 2,
        "baudrate": 9600,
        "parity": None,
        "bits": 8,
        "stop": 1
    }
}

with open("config.json", 'w') as file:
	json.dump(config, file, indent=4)
