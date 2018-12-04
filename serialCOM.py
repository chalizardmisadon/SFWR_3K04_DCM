import serial
import serial.tools.list_ports
import time
import struct


ser = serial.Serial(port="COM4", baudrate=115200)

echoParameterStr = "\x16\x22" + "\x00"*38
echoParameterByte = str.encode(echoParameterStr)

echoIDStr = "\x16\x33" + "\x00"*38
echoIDByte = str.encode(echoIDStr)

resetIDStr = "\x16\x35" + "\x00"*38
resetIDByte = str.encode(resetIDStr)

egramStartStr = "\x16\x66" + "\x00"*38
egramStartByte = str.encode(egramStartStr)

writeZeroStr = "\x16\x55" + "VVIR" + "\x00"*34
writeZeroByte = str.encode(writeZeroStr)

SYNC = str.encode("\x16")
WRITE = str.encode("\x55")

Lower_Rate = 50
Upper_Rate = 60
Max_Sensor = 130
AV_Delay = 30

ATR_Amplitude = 35
ATR_Width = 100
VENT_Amplitude = 40
VENT_Width = 100

ATR_Sense = 30
VENT_Sense = 27
ATR_Refractory = 0
VENT_Refractory = 0
AV_Refractory = 0

Activity_Threshold = 0
Reaction_Time = 0
Response_Factor = 0
Recovery_Time = 1

intArray = [Lower_Rate, Upper_Rate, Max_Sensor, AV_Delay, \
            ATR_Amplitude, ATR_Width, VENT_Amplitude, VENT_Width, \
            ATR_Sense, VENT_Sense, ATR_Refractory, VENT_Refractory, AV_Refractory, \
            Activity_Threshold, Reaction_Time, Response_Factor, Recovery_Time]

intArrayByte = [ i.to_bytes(2, 'little') for i in intArray ]
intByte = b''

for i in intArrayByte:
    intByte = intByte + i

print(intByte.hex(), len(intByte), type(intByte))

modeStr = "VVIR"
modeByte = str.encode(modeStr)

print(modeByte.hex(), len(modeByte), type(modeByte))
print()

cmdByte = SYNC + WRITE + modeByte + intByte
print(cmdByte, len(cmdByte), type(cmdByte))
print("=============================")
print()

testCmd = str.encode("\x16\x45\x55\x01" + "\x00"*54)

##print(ser.write(resetIDByte))

print(ser.write(egramStartByte))
while True:
    inData = ser.read(40)
    A1 = chr(inData[0])
    Anum1 = struct.unpack('<d', inData[1:9])[0]
    B1 = chr(inData[9])
    Bnum1 = struct.unpack('<d', inData[10:18])[0]
    A2 = chr(inData[18])
    Anum2 = struct.unpack('<d', inData[19:27])[0]
    B2 = chr(inData[27])
    Bnum2 = struct.unpack('<d', inData[28:36])[0]
    
    print(A1, Anum1, B1, Bnum1, A2, Anum2, B2, Bnum2)
    print(type(Anum1))

##
##time.sleep(2)
##print(ser.write(echoIDByte))
##inData = ser.read(40)
##print(inData, len(inData), type(inData))


def serialEchoID():
    echoIDStr = "\x16\x33" + "\x00"*38
    echoIDByte = str.encode(echoIDStr)
    print(ser.write(echoIDByte))
    time.sleep(1)

def serialEchoParameter():
    echoParameterStr = "\x16\x22" + "\x00"*38
    echoParameterByte = str.encode(echoParameterStr)
    print(ser.write(echoParameterByte))
    time.sleep(1)

def serialWriteParameter():
    SYNC = str.encode("\x16")
    WRITE = str.encode("\x55")
    
    Lower_Rate = 130
    Upper_Rate = 60
    Max_Sensor = 130
    AV_Delay = 30

    ATR_Amplitude = 35
    ATR_Width = 100
    VENT_Amplitude = 40
    VENT_Width = 100

    ATR_Sense = 25
    VENT_Sense = 25
    ATR_Refractory = 0
    VENT_Refractory = 0
    AV_Refractory = 0

    Activity_Threshold = 0
    Reaction_Time = 0
    Response_Factor = 0
    Recovery_Time = 1

    intArray = [Lower_Rate, Upper_Rate, Max_Sensor, AV_Delay, \
                ATR_Amplitude, ATR_Width, VENT_Amplitude, VENT_Width, \
                ATR_Sense, VENT_Sense, ATR_Refractory, VENT_Refractory, AV_Refractory, \
                Activity_Threshold, Reaction_Time, Response_Factor, Recovery_Time]
    
    intByte = b''
    for i in intArray:
        intByte = intByte + i.to_bytes(2, 'little')
        
    cmdByte = SYNC + WRITE + modeByte + intByte
    print(ser.write(cmdByte))
    time.sleep(1)


'''
##comPort = serial.tools.list_ports.grep("UART")
##uartPort = {}
##for p in comPort:
##    uartPort[p.device] = p.description
##print(uartPort)
##print(bool(uartPort))
##for p in uartPort:
##    print(p)

        
##print([[p.description, p.device] for p in comPort])
##print([p.device for p in comPort])


##print([p.description for p in serial.tools.list_ports.grep("UART")])
ser = serial.Serial(port="COM4", baudrate=115200)
ser.timeout = 0.1
inData = ser.read(40)
print(inData, len(inData))
'''


class appDCM:

    def listValidComPort(self):
        portDescription = "UART"
        comPort = serial.tools.list_ports.grep(portDescription)
        self.uartPort = {}
        for p in comPort:
            self.uartPort[p.device] = p.description
        return bool(self.uartPort)
    
    def getValidPacemaker(self):
        for p in self.uartPort:
            self.port = serial.Serial(port=p, baudrate=115200)
            self.port.timeout = 1
            self.serialEchoID(self.port)
            self.pacemakerID = str(self.serialReadData(self.port))
            print(self.pacemakerID, type(self.pacemakerID))
            if "42069" in self.pacemakerID:
                print(p, "is a valid pacemaker")
                return True
            else:
                print(p, "is not valid pacemaker")
        return False

    def serialEchoID(self, port):
        echoIDStr = "\x16\x33" + "\x00"*38
        echoIDByte = str.encode(echoIDStr)
        port.write(echoIDByte)


    def serialReadData(self, port):
        return port.read(40)

##login = appDCM()
##print(login.listValidComPort())
##login.getValidPacemaker()
##time.sleep(2)
##print(login.port)
