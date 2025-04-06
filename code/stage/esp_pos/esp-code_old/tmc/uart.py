from machine import UART
import struct, time

class TMC_UART:

    rFrame  = [0x55, 0, 0, 0]
    wFrame  = [0x55, 0, 0, 0, 0, 0, 0, 0]

    def __init__(self, config):

        self.config = config

        # Initialize serial communication
        port = self.config["UART"]["port"]
        baudrate = self.config["UART"]["baudrate"]
        parity = self.config["UART"]["parity"]
        bits = self.config["UART"]["bits"]
        stop = self.config["UART"]["stop"]

        self.communication_pause = 500/baudrate

        self.serial = UART(port, baudrate)
        self.serial.init(baudrate, bits=bits, parity=parity, stop=stop)

    def __del__(self):
        self.serial.close()

    def compute_crc8_atm(self, datagram, init_val=0):
        crc = init_val
        # Iterate bytes in data
        for byte in datagram:
            # Iterate bits in byte
            for _ in range(8):
                if (crc >> 7) ^ (byte & 0x01):
                    crc = ((crc << 1) ^ 0x07) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
                # Shift to next bit
                byte = byte >> 1
        return crc

    def read_reg(self, mtr_id, reg):
        
        rtn = ""
        
        self.rFrame[1] = mtr_id
        self.rFrame[2] = reg
        self.rFrame[3] = self.compute_crc8_atm(self.rFrame[:-1])

        rt = self.serial.write(bytes(self.rFrame))
        if rt != len(self.rFrame):
            print("TMC2209: Err in write {}".format(__), file=sys.stderr)
            return False
        time.sleep(self.communication_pause)
        if self.serial.any():
            rtn = self.serial.read()
        time.sleep(self.communication_pause)
        if rtn == None:
            print("TMC2209: Err in read")
            return ""
        return(rtn[7:11])

    def read_int(self, mtr_id, reg):
        tries = 0
        while(True):
            rtn = self.read_reg(mtr_id, reg)
            tries += 1
            if(len(rtn)>=4):
                break
            else:
                print("TMC2209: did not get the expected 4 data bytes. Instead got "+str(len(rtn))+" Bytes")
            if(tries>=10):
                print("TMC2209: after 10 tries not valid answer. exiting")
                print("TMC2209: is Stepper Powersupply switched on ?")
                raise SystemExit
        val = struct.unpack(">i",rtn)[0]
        return(val)

    def write_reg(self, mtr_id, reg, val):
        
        self.wFrame[1] = mtr_id
        self.wFrame[2] =  reg | 0x80
        
        self.wFrame[3] = 0xFF & (val>>24)
        self.wFrame[4] = 0xFF & (val>>16)
        self.wFrame[5] = 0xFF & (val>>8)
        self.wFrame[6] = 0xFF & val
        
        self.wFrame[7] = self.compute_crc8_atm(self.wFrame[:-1])

        rtn = self.serial.write(bytes(self.wFrame))
        if rtn != len(self.wFrame):
            print("TMC2209: Err in write {}".format(__), file=sys.stderr)
            return False
        time.sleep(self.communication_pause)

        return(True)

    def write_reg_check(self, mtr_id, reg, val):
        IFCNT           =   0x02

        ifcnt1 = self.read_int(mtr_id, IFCNT)
        self.write_reg(mtr_id, reg, val)
        ifcnt2 = self.read_int(mtr_id, IFCNT)
        ifcnt2 = self.read_int(mtr_id, IFCNT)
        
        if(ifcnt1 >= ifcnt2):
            print("TMC2209: writing not successful!")
            print(f"reg:{reg} val:{val}")
            print("ifcnt:",ifcnt1,ifcnt2)
            return False
        else:
            return True

    #-----------------------------------------------------------------------
    # this sets a specific bit to 1
    #-----------------------------------------------------------------------
    def set_bit(self, value, bit):
        return value | (bit)

    #-----------------------------------------------------------------------
    # this sets a specific bit to 0
    #-----------------------------------------------------------------------
    def clear_bit(self, value, bit):
        return value & ~(bit)
