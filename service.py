import serial
import os
import time
import subprocess
import logging
import threading
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import signal

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, signum, frame):
    self.kill_now = True
    log.info('UPS service is being stopped')

class UPS:
    def __init__(self):
        ups_loc = subprocess.check_output(['sudo','/bin/bash','kill.sh'])
        ups_loc = ups_loc.decode("UTF-8")
        ups_loc = ups_loc.replace("\n", "")
        self.ser = serial.Serial(ups_loc, 9600)

    def get_firmver(self):
        return self.__get('@Fx#').replace("F","").replace("-",".")

    def get_curvol(self):
        return self.__get('@V0#').replace("V","")

    def get_chargestat(self):
        a = self.__get('@C0#').replace("","")
        if a == "CF0C0":
            return "err"
        elif a == "CF1C0":
            return "chg"
        elif a == "CF0C1":
            return "full"
        elif a == "CF1C1":
            return "dch"

    def shutdown(self):
        self.__get('@Px#')

    def __get(self,a):
        a = bytes(a, 'utf-8')
        self.ser.write(a)
        a = self.ser.readline().decode("UTF-8")
        a = a.replace("\n", "")
        a = a.replace("\r", "")
        a = a.replace("#", "")
        a = a.replace("@", "")
        return(a)

class Logger:
    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Z %Y:%m:%d %H:%M:%S')
        file_handler = RotatingFileHandler('./log/ups.log', maxBytes=1024*1024*10, backupCount=10)
        file_handler.setFormatter(formatter)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(consoleHandler)
    
    def debug(self,message):
        self.logger.debug(message)

    def info(self,message):
        self.logger.info(message)

    def warn(self,message):
        self.logger.warning(message)

    def error(self,message):
        self.logger.error(message)

    def crit(self,message):
        self.logger.critical(message)

killer = GracefulKiller()
log = Logger()
log.info('UPS service is starting')
ups = UPS()

try:
    import pwmio
    import board
    log.info('gpio module import success')
except:
    log.warn('gpio module import failed buzzer not working')
    log.warn('Create a dummy class')
    #Dummy class
    class Alarm:
        def __init__(self):
            pass

        def on(self):
            pass

        def off(self):
            pass
else:
    try:
        class Alarm:
            def __init__(self):
                self.piezo = pwmio.PWMOut(board.D15, variable_frequency=True)
                self.piezo.duty_cycle = 0
                self.piezo.frequency = 523

            def on(self):
                self.piezo.duty_cycle = 50000

            def off(self):
                self.piezo.duty_cycle = 0
    except:
        log.crit('gpio pin assignment failure')
        log.warn('Create a dummy class')
        #Dummy class
        class Alarm:
            def __init__(self):
                pass

            def on(self):
                pass

            def off(self):
                pass

buz = Alarm()

buz.on()
log.info('UPS service started successfully')
log.info(f"UPS Firmware Ver {ups.get_firmver()}")
time.sleep(0.3)
buz.off()

while not killer.kill_now:
    ps = ups.get_chargestat()

    if ps == "full":
        log.info("AC power active")
    elif ps == "chg":
        log.info('AC power restored Charging')
    elif ps == "dch":
        buz.on()
        log.warn('AC power loss')
        pw = int(ups.get_curvol())
        if pw <= 3500:
            log.crit('battery is too low Shut down system')
            ups.shutdown()
            os.system("shutdown now")
        elif pw <= 3650:
            log.crit('battery is too low')
        elif pw <= 3800:
            log.warn('battery is low')
    elif ps == "err":
        log.crit('UPS hardware error detect')

    log.info("Current Voltage "+ups.get_curvol()+"mV")
    time.sleep(0.5)
    buz.off()
    time.sleep(0.5)
buz.off()
log.info('UPS service stopped successfully')
