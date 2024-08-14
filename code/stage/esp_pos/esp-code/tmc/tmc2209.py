from . import reg
import math

class TMC_2209:
    
    def __init__(self, tmc_uart, mtr_id=0):
        
        self.tmc_uart = tmc_uart
        self.mtr_id = mtr_id
        
    def get_mstep(self):
        
        chopconf = self.tmc_uart.read_int(self.mtr_id, reg.CHOPCONF)
        msresdezimal = chopconf & (reg.msres0 | reg.msres1 | reg.msres2 | reg.msres3)
        msresdezimal = msresdezimal >> 24
        msresdezimal = 8 - msresdezimal
        return int(math.pow(2, msresdezimal))
    
    def get_direction(self):
        gconf = self.tmc_uart.read_int(self.mtr_id, reg.GCONF)
        return (gconf & reg.shaft)
    
    #-----------------------------------------------------------------------
    # return whether Vref (1) or 5V (0) is used for current scale
    #-----------------------------------------------------------------------
    def get_iscale_analog(self):
        gconf = self.tmc_uart.read_int(self.mtr_id, reg.GCONF)
        return (gconf & reg.i_scale_analog)
    
    #-----------------------------------------------------------------------
    # returns which sense resistor voltage is used for current scaling
    # 0: Low sensitivity, high sense resistor voltage
    # 1: High sensitivity, low sense resistor voltage
    #-----------------------------------------------------------------------
    def get_vsense(self):
        chopconf = self.tmc_uart.read_int(self.mtr_id, reg.CHOPCONF)
        return (chopconf & reg.vsense)
    
    #-----------------------------------------------------------------------
    # sets the current scale (CS) for Running and Holding
    # and the delay, when to be switched to Holding current
    # IHold = 0-31; IRun = 0-31; IHoldDelay = 0-15
    #-----------------------------------------------------------------------
    def set_irih(self, IHold=15, IRun=15, IHoldDelay=15):
        
        ihold_irun = 0
        ihold_irun = ihold_irun | IHold << 0
        ihold_irun = ihold_irun | IRun << 8
        ihold_irun = ihold_irun | IHoldDelay << 16
        self.tmc_uart.write_reg_check(self.mtr_id, reg.IHOLD_IRUN, ihold_irun)
