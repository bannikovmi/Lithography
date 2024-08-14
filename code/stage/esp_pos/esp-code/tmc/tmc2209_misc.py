    def get_status(self):
        print("---")
        print(f"drive {self.mtr_id} DRIVER STATUS:")
        drvstatus = self.tmc_uart.read_int(self.mtr_id, reg.DRVSTATUS)
        if(drvstatus & reg.stst):
            print("TMC2209: Info: motor is standing still")
        else:
            print("TMC2209: Info: motor is running")

        if(drvstatus & reg.stealth):
            print("TMC2209: Info: motor is running on StealthChop")
        else:
            print("TMC2209: Info: motor is running on SpreadCycle")

        cs_actual = drvstatus & reg.cs_actual
        cs_actual = cs_actual >> 16
        print("TMC2209: CS actual: "+ str(cs_actual))

        if(drvstatus & reg.olb):
            print("TMC2209: Warning: Open load detected on phase B")
        
        if(drvstatus & reg.ola):
            print("TMC2209: Warning: Open load detected on phase A")
        
        if(drvstatus & reg.s2vsb):
            print("TMC2209: Error: Short on low-side MOSFET detected on phase B. The driver becomes disabled")

        if(drvstatus & reg.s2vsa):
            print("TMC2209: Error: Short on low-side MOSFET detected on phase A. The driver becomes disabled")

        if(drvstatus & reg.s2gb):
            print("TMC2209: Error: Short to GND detected on phase B. The driver becomes disabled. ")
        
        if(drvstatus & reg.s2ga):
            print("TMC2209: Error: Short to GND detected on phase A. The driver becomes disabled. ")
        
        if(drvstatus & reg.ot):
            print("TMC2209: Error: Driver Overheating!")
        
        if(drvstatus & reg.otpw):
            print("TMC2209: Warning: Driver Overheating Prewarning!")
        
        print("---")
        return drvstatus
    
    def get_gconf(self):
        print("TMC2209: ---")
        print(f"drive {self.mtr_id}: GENERAL CONFIG")
        gconf = self.tmc_uart.read_int(self.mtr_id, reg.GCONF)

        if(gconf & reg.i_scale_analog):
            print("TMC2209: Driver is using voltage supplied to VREF as current reference")
        else:
            print("TMC2209: Driver is using internal reference derived from 5VOUT")
        if(gconf & reg.internal_rsense):
            print("TMC2209: Internal sense resistors. Use current supplied into VREF as reference.")
            print("TMC2209: VREF pin internally is driven to GND in this mode.")
            print("TMC2209: This will most likely destroy your driver!!!")
            raise SystemExit
        else:
            print("TMC2209: Operation with external sense resistors")
        if(gconf & reg.en_spreadcycle):
            print("TMC2209: SpreadCycle mode enabled")
        else:
            print("TMC2209: StealthChop PWM mode enabled")
        if(gconf & reg.shaft):
            print("TMC2209: Inverse motor direction")
        else:
            print("TMC2209: normal motor direction")
        if(gconf & reg.index_otpw):
            print("TMC2209: INDEX pin outputs overtemperature prewarning flag")
        else:
            print("TMC2209: INDEX shows the first microstep position of sequencer")
        if(gconf & reg.index_step):
            print("TMC2209: INDEX output shows step pulses from internal pulse generator")
        else:
            print("TMC2209: INDEX output as selected by index_otpw")
        if(gconf & reg.mstep_reg_select):
            print("TMC2209: Microstep resolution selected by MSTEP register")
        else:
            print("TMC2209: Microstep resolution selected by pins MS1, MS2")
        
        print("TMC2209: ---")
        return gconf
    
    def get_gstat(self):
        print("TMC2209: ---")
        print("TMC2209: GSTAT")
        gstat = self.tmc_uart.read_int(self.mtr_id, reg.GSTAT)
        if(gstat & reg.reset):
            print("TMC2209: The Driver has been reset since the last read access to GSTAT")
        if(gstat & reg.drv_err):
            print("TMC2209: The driver has been shut down due to overtemperature or short circuit detection since the last read access")
        if(gstat & reg.uv_cp):
            print("TMC2209: Undervoltage on the charge pump. The driver is disabled in this case")
        print("TMC2209: ---")
        return gstat
    
    def get_ioin(self):
        print("TMC2209: ---")
        print("TMC2209: INPUTS")
        ioin = self.tmc_uart.read_int(self.mtr_id, reg.IOIN)

        if(ioin & reg.io_spread):
            print("TMC2209: spread is high")
        else:
            print("TMC2209: spread is low")

        if(ioin & reg.io_dir):
            print("TMC2209: dir is high")
        else:
            print("TMC2209: dir is low")

        if(ioin & reg.io_step):
            print("TMC2209: step is high")
        else:
            print("TMC2209: step is low")

        if(ioin & reg.io_enn):
            print("TMC2209: en is high")
        else:
            print("TMC2209: en is low")
        
        print("TMC2209: ---")
        return ioin
    
    def get_chopconf(self):
        print("TMC2209: ---")
        print("TMC2209: CHOPPER CONTROL")
        chopconf = self.tmc_uart.read_int(self.mtr_id, reg.CHOPCONF)
        
        print("TMC2209: native "+str(self.getMicroSteppingResolution())+" microstep setting")
        
        if(chopconf & reg.intpol):
            print("TMC2209: interpolation to 256 microsteps")
        
        if(chopconf & reg.vsense):
            print("TMC2209: 1: High sensitivity, low sense resistor voltage")
        else:
            print("TMC2209: 0: Low sensitivity, high sense resistor voltage")

        print("TMC2209: ---")
        return chopconf