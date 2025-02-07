import json
with open("config//config.json", "r") as file:
    config = json.load(file)

from tmc.uart import TMC_UART
from tmc.tmc2209 import TMC_2209


mtr_id = 3 # Lense
tmc_uart = TMC_UART(config)
drz = TMC_2209(tmc_uart, mtr_id)

from tmc import reg
drvstatus = tmc_uart.read_int(mtr_id, reg.DRVSTATUS)
if(drvstatus & reg.stst):
    print("TMC2209: Info: motor is standing still")
else:
    print("TMC2209: Info: motor is running")

drz.set_irih(IHold=0, IRun=0, IHoldDelay=0)




# pin_step = 32
# pin_dir = 33
# pin_en = 5
# 
# tmc_2209 = TMC_2209(pin_step, pin_dir, pin_en)
