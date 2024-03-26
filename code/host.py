import pyvisa
import time

rm = pyvisa.ResourceManager()
esp32 = rm.open_resource('ASRL4::INSTR')
esp32.baud_rate = 115200
esp32.write_termination = '\r\n'
esp32.read_termination = '\r\n'
esp32.timeout = 1000

direction = 0
nsteps = 10
step_delay = 100

esp32.write("ESP_MV_0_10_2")
