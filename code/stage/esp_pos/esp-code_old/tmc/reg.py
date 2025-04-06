#-----------------------------------------------------------------------
# this file contains:
# 1. hexadecimal address of the different registers
# 2. bitposition and bitmasks of the different values of each register
#
# Example:
# the register IOIN has the address 0x06 and the first bit shows
# whether the ENABLE (EN/ENN) Pin is currently HIGH or LOW
#-----------------------------------------------------------------------

#addresses
GCONF           =   0x00
GSTAT           =   0x01
IFCNT           =   0x02 # Successful UART interface access counter
SLAVECONF       =   0x03 # Send delay for read access (time until reply is sent)
OTP_PROG        =   0x04 # OTP programming
OTP_READ        =   0x05 # Access to OTP memory result and update
IOIN            =   0x06
IHOLD_IRUN      =   0x10
TSTEP           =   0x12
TCOOLTHRS       =   0x14
SGTHRS          =   0x40
SG_RESULT       =   0x41
MSCNT           =   0x6A
CHOPCONF        =   0x6C
DRVSTATUS       =   0x6F

#GCONF -- General config
i_scale_analog      = 1<<0 # Current reference (external ref on VREF or internal ref from 5V) 
internal_rsense     = 1<<1 # Internal or external sense resistors
en_spreadcycle      = 1<<2 # Spreadcycle or Stealthchop PWM mode enabled
shaft               = 1<<3 # Inverse or normal motor direction
index_otpw          = 1<<4 # INDEX pin configuration (OT prewarning or first microstep position of sequencer)
index_step          = 1<<5 # INDEX output (step pulses from internal pulse generator or by index_otpw)
mstep_reg_select    = 1<<7 # Microstep resolution (by MSTEP reg or by pins MS1, MS2)

#GSTAT -- Global status flags
reset               = 1<<0 # Driver has been reset
drv_err             = 1<<1 # Driver has been shut down due to OT or short circuit
uv_cp               = 1<<2 # Undervoltage on the charge pump

#CHOPCONF -- Chopper control
vsense              = 1<<17 # High sensitivity, low sense res voltage or Low sensitivity, high sense res voltage
msres0              = 1<<24 # 
msres1              = 1<<25
msres2              = 1<<26
msres3              = 1<<27
intpol              = 1<<28 # Interpolation to 256 microsteps
dedge               = 1<<29 # Enable double edge step pulses
diss2g              = 1<<30 # Short to GND protection disable
diss2vs             = 1<<31 # Low side short protection disable

#IOIN -- Driver input pins state
io_enn              = 1<<0 # Enable pin is HIGH or LOW 
io_step             = 1<<7 # Step pin is HIGH or LOW
io_spread           = 1<<8 # Spread pin is HIGH or LOW
io_dir              = 1<<9 # Dir pin is HIGH or LOW

#DRVSTATUS
stst                = 1<<31 # Standing still
stealth             = 1<<30 # Stealthchop or spreadcycle modes
cs_actual           = 31<<16 # Actual current control scaling
t157                = 1<<11 # 157°C comparator
t150                = 1<<10 # 150°C comparator
t143                = 1<<9 # 143°C comparator
t120                = 1<<8 # 120°C comparator
olb                 = 1<<7 # Open load on phase B
ola                 = 1<<6 # Open load on phase A
s2vsb               = 1<<5 # Short on low-side MOSFET on phase B
s2vsa               = 1<<4 # Short on low-side MOSFET on phase A
s2gb                = 1<<3 # Short to GND on phase B
s2ga                = 1<<2 # Short to GND on phase A
ot                  = 1<<1 # Overheating
otpw                = 1<<0 # Overheating prewarning

#IHOLD_IRUN
ihold               = 31<<0
irun                = 31<<8
iholddelay          = 15<<16

#SGTHRS
sgthrs              = 255<<0

#others
mres_256 = 0
mres_128 = 1
mres_64 = 2
mres_32 = 3
mres_16 = 4
mres_8 = 5
mres_4 = 6
mres_2 = 7
mres_1 = 8
