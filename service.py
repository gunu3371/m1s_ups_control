import serial
import os
import time
import subprocess
import pwmio
import board
import multiprocessing

piezo = pwmio.PWMOut(board.D15, variable_frequency=True)
piezo.duty_cycle = 0
piezo.frequency = 523

ups_loc = subprocess.check_output(['sudo','/bin/bash','kill.sh'])
ups_loc = ups_loc.decode("UTF-8")
ups_loc = ups_loc.replace("\n", "")
ser = serial.Serial(ups_loc, 9600)

def swr(a):
    a = bytes(a, 'utf-8')
    ser.write(a)
    a = ser.readline().decode("UTF-8")
    a = a.replace("\n", "")
    a = a.replace("\r", "")
    a = a.replace("#", "")
    a = a.replace("@", "")
    return(a)
    
prt = str()
while True:
    print("------------------------------------------------------")
    print("------------------------------------------------------")
    a = swr('@Fx#').replace("F","")
    print("firmware ver ",a)
    vol = swr('@V0#').replace("V","")
    print("current voltage "+vol+"mV")
    a = swr('@C0#').replace("","")
    if a != "CF1C1":
        piezo.duty_cycle = 0
        print("Power Status Normal")
    elif a == "CF0C0":
        print("UPS !ERROR!")
    else:
        print("Power Loss Detect")
        piezo.duty_cycle = 45000
        if int(vol) <= 3600:
            ser.write(b'@Px#')
            os.system("shutdown now")
    print("------------------------------------------------------")
    print("------------------------------------------------------")
    time.sleep(1)
    piezo.duty_cycle = 0
    time.sleep(1)