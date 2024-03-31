import json

drives = {
	"DRX": {
	"is_at_max": False,
	"is_at_min": False,
	},

	"DRY": {
		"is_at_max": False,
		"is_at_min": False,
	},

	"DRZ": {
		"is_at_max": False,
		"is_at_min": False,
	},

	"DRL": {
		"is_at_max": False,
		"is_at_min": False,
	}
}

with open("config.json", 'w') as file:
	json.dump(drives, file, indent=4)
