import serial
import os
import time
import subprocess
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import signal
import socket
import json
import datetime

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
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Z %Y/%m/%d %H:%M:%S')
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

class PowerDB:
    def __init__(self):
        self.dbname = './powerdb.json'
        if not 'data' in json.load(self.dbname):
            json.dump({'data':[]},self.dbname)

    def offline(self):
        db = json.load(self.dbname)
        db['data'].append({'time':datetime.datetime.now(datetime.UTC).strftime("%Y/%m/%d %H:%M:%S.%f %Z"),'status':'offline','ACstat':False})
        json.dump({'data':db},self.dbname)

    def online(self):
        db = json.load(self.dbname)
        db['data'].append({'time':datetime.datetime.now(datetime.UTC).strftime("%Y/%m/%d %H:%M:%S.%f %Z"),'status':'online','ACstat':True})
        json.dump({'data':db},self.dbname)

    def lastoff(self):
        db = json.load(self.dbname)
        for i in reversed(db['data']):
            if i['ACstat'] == True:
                lof = i['time']
        lof = time.strptime(lof, '%Y/%m/%d %H:%M:%S.%f %Z')
        ntime = datetime.datetime.now(datetime.UTC)

class Broadcast:
    def __init__(self,broadcast_ip='255.255.255.255',port=51547):
        self.broadcast_ip = broadcast_ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send(self,message:dict):
        message = json.dumps(message)
        encoded_message = self.__hamming_encode(''.join(format(ord(c), '08b') for c in message))
        self.sock.sendto(encoded_message.encode('utf-8'), (self.broadcast_ip, self.port))

    @staticmethod
    def __hamming_encode(data):
        data_bits = [int(bit) for bit in data]
        m = len(data_bits)
        r = 1

        while (2 ** r) < (m + r + 1):
            r += 1

        hamming_code = [0] * (m + r)
        j = 0
        for i in range(1, m + r + 1):
            if i == 2 ** j:
                j += 1
            else:
                hamming_code[i - 1] = data_bits.pop(0)

        for i in range(r):
            position = 2 ** i
            value = 0
            for j in range(1, m + r + 1):
                if j & position and j != position:
                    value ^= hamming_code[j - 1]
            hamming_code[position - 1] = value

        return ''.join(map(str, hamming_code))

    @staticmethod
    def __hamming_decode(data):
        data_bits = [int(bit) for bit in data]
        m = len(data_bits)
        r = 0

        while (2 ** r) < m:
            r += 1

        error_pos = 0
        for i in range(r):
            position = 2 ** i
            value = 0
            for j in range(1, m + 1):
                if j & position:
                    value ^= data_bits[j - 1]
            if value:
                error_pos += position

        if error_pos:
            data_bits[error_pos - 1] ^= 1

        decoded_data = []
        j = 0
        for i in range(1, m + 1):
            if i != 2 ** j:
                decoded_data.append(data_bits[i - 1])
            else:
                j += 1

        return ''.join(map(str, decoded_data))


killer = GracefulKiller()
log = Logger()
log.info('UPS service is starting')
ups = UPS()
broad = Broadcast()
# ac = PowerDB()

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
    broad.send({'msg':'test'})
buz.off()
log.info('UPS service stopped successfully')
