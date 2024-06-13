import pyvisa

rm = pyvisa.ResourceManager("@py")
ESP = rm.open_resource("ASRL4::INSTR")

ESP.baud_rate = 115200
ESP.write_termination = '\r\n'
ESP.read_termination = '\r\n'
ESP.timeout = 2000

while True:
	try:
		print(ESP.read())
	except pyvisa.errors.VisaIOError:
		print("error")