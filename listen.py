import serial
import serial.tools.list_ports as sp
from threading import Thread
from time import sleep

class Serial():
    def __init__(self,data):
        #/dev/ttyUSB1
        self.data = data
        self.interval = 0.5 # 0.1 second
        self.stop = False
        self.CR = '\r' #carriage return
        self.LF = '\n' #line feed
        self.STX = '\x02' #<STX> for temperature
    def listen(self):
        self.thread_t = Thread(target = self.listen_device,args=("temp",))
        self.thread_v = Thread(target = self.listen_device,args=("vaccum",))
        self.thread_l = Thread(target = self.listen_device,args=("laser",))
        self.thread_s = Thread(target = self.listen_device,args=("stepper",))
        self.thread_lc = Thread(target = self.listen_command,args=("listencommand",))
        self.thread_p = Thread(target = self.listen_port)
        self.thread_v.start()
        self.thread_t.start()
        self.thread_l.start()
        self.thread_s.start()
        self.thread_lc.start()
        self.thread_p.start()
    def listen_device(self,device):
        while True:
            if self.stop == True:
                return 0
            if self.data[device]['port'] != 'none': 
                try:
                    vac = serial.Serial(port=self.data[device]['port'],
                                        baudrate=9600,timeout=2)
                    self.data[device]['port'] = vac.port
                except:
                    self.data[device]['port'] = 'none'
                while self.data[device]['port'] != 'none':
                    if self.stop == True:
                        vac.close()
                        return 0
                    #func line#
                    if self.data[device]['fault'] > 5:
                        self.data[device]['port'] = 'none'
                        self.data[device]['fault'] = 0
                        break
                    command = self.data[device]['command']
                    self.data[device]['command'] = []
                    listencommand = self.data[device]['listencommand']
                    self.send(vac,device,command,True)
                    self.send(vac,device,listencommand,False)
                    #func line#
                    sleep(self.interval)
            sleep(1)
    def send(self,port,device,command,mode):
        buffer = []
        if mode == True:
            if command == []:
                return 0
            name = 'result'
            for cm in command:
                if cm == '':
                    continue
                buffer = []
                cm = cm.split('%')
                addr = cm[-1] #string
                cm = cm[:-1]
                for c in cm:
                    try:
                        cm_t,until = self.sendtype(c,device)
                        port.flushInput()
                        port.write(cm_t.encode('ASCII'))
                        temp = c+'%'
                        sleep(0.05)
                        while True:
                            receive = port.read_until(until).decode('ASCII')[:-len(until)]
                            temp += receive+'%'
                            if port.inWaiting(): continue
                            break
                        buffer.append(temp[:-1])
                    except:
                        self.data[device]['port'] = 'none'
                try:
                    pass
                    self.data[device][name][addr].append(buffer)
                except:
                    self.data[device][name][addr] = buffer
        else:
            name = 'listen_result'
            for cm in command:
                if cm == '':
                    continue
                try:
                    cm_t,until = self.sendtype(cm,device)
                    port.flushInput()
                    port.write(cm_t.encode('ASCII'))
                    temp = cm+'%'
                    sleep(0.05)
                    while True:
                        receive = port.read_until(until).decode('ASCII')[:-len(until)]
                        temp += receive+'%'
                        if port.inWaiting(): continue
                        if len(temp) <= len(cm)+2:
                            self.data[device]['fault'] += 1
                        else:
                            self.data[device]['fault'] = 0
                        break
                    buffer.append(temp[:-1])
                except:
                    self.data[device]['port'] = 'none'
            self.data[device][name] = buffer
    def listen_command(self,name):
        #mode=0:read & remove,mode=1:just read
        while self.stop == False:
            try:
                f = open('data/'+name,'r',encoding='utf-8')
            except FileNotFoundError:
                f = open('data/'+name,'w',encoding='utf-8')
                f.close()
                f = open('data/'+name,'r',encoding='utf-8')
            finally:
                lines = f.readlines()
                for line in lines:
                    temp = line[:-1].split('%')
                    device =  temp[0]
                    command = temp[1:]
                    self.data[device][name] = command
                f.close()
            sleep(0.1)
    def listen_port(self):
        no = ['/dev/ttyS0','/dev/ttyAMA0'] #do not use
        while True:
            ports = self.port()
            for device in no:
                try:
                    ports.remove(device)
                except:
                    continue
            #print(ports)
            for port_ in ports:
                #if port_[-4:] == 'USB0':
                #    self.data['stepper']['port'] = port_
                if self.stop == True:
                    return 0
                command = "\x0201DRS\r\n"
                try:
                    a = True
                    for device in list(self.data.keys()):
                        if self.data[device]['port'] == port_:
                            a = False
                    if a == True:
                        com = serial.Serial(port=port_,baudrate=9600,timeout=1)
                        sleep(2)
                        com.write(command.encode('utf-8'))
                        sleep(0.2)
                        line = com.read_until(b'\r').decode('utf-8')
                        #print(port_,line.encode('utf-8'))
                        com.close()
                        if line == '\x15\r':
                            self.data['vaccum']['port'] = port_
                        elif line == '\x0201NG08\r' or line == "\x0201DRS\r":
                            self.data['temp']['port']   = port_
                        elif line == '2\r':
                            self.data['laser']['port']  = port_
                        elif line == 'BAD COMMAND=\x0201DRS\r':
                            self.data['stepper']['port']= port_
                        else:
                            pass
                except:
                    print("??")
                    continue
            sleep(0.5)

    def sendtype(self,c,t):
        if   t == 'temp':
            return self.STX+c+self.CR+self.LF,b'\r\n'
        elif t == 'vaccum':
            return c+self.CR+self.LF+'\x05',b'\r\n'
        elif t == 'laser':
            return c + self.CR,b'\r'
        elif t == 'stepper':
            return c + self.LF,b'\n'
        else:
            return c + self.LF,b'\n'
    def port(self):
        temp = []
        portlist = sp.comports()
        for p in portlist:
            temp.append(p[0])
        return temp
    def off(self):
        self.stop = True
        self.thread_v.join()
        self.thread_p.join()
        print("terminated...")
        self.stop = False

