from machine import UART

class TMC_UART:

    rFrame  = [0x55, 0, 0, 0]
    wFrame  = [0x55, 0, 0, 0, 0, 0, 0, 0]

	def __init__(self, config):

		self.config = config
		uart_id = config["UART"]["id"]
		baudrate = config["UART"]["baudrate"]
		bits = config["UART"]["bits"]
		parity = config["UART"]["parity"]
		stop = config["UART"]["stop"]

		self.uart = UART(uart_id, baudrate)
		self.uart.init(baudrate, bits=bits, parity=parity, stop=stop)
		self.com_pause = 500/baudrate

	def __del__(self):

		self.uart.close()

    def compute_crc8_atm(self, datagram, initial_value=0):
        crc = initial_value
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

    def read_reg(self, drive_id, reg):

        rtn = ""
        
        self.rFrame[1] = drive_id
        self.rFrame[2] = reg
        self.rFrame[3] = self.compute_crc8_atm(self.rFrame[:-1])

       	rt = self.uart.write(bytes(self.rFrame))
        if rt != len(self.rFrame):
            print("TMC2209: Err in write")
            return False
        time.sleep(self.communication_pause)
        
        if self.uart.any():
            rtn = self.uart.read() # read what it self 
        time.sleep(self.communication_pause)
        if rtn == None:
            print("TMC2209: Err in read")
            return ""
        return(rtn[7:11])