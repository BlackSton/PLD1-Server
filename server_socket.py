import socket
from _thread import *
from threading import Thread
import time

class tcp():
    def __init__(self,data):
        self.data = data
        self.close  = False
        ss = Thread(target = self.run)
        ss.start()
    def run(self):
        self.HOST = '192.168.0.101'#'127.0.0.1'
        self.PORT = 9889
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.server_socket.bind((self.HOST,self.PORT))
        self.server_socket.listen()
        print("server start")
        while True:
            try:
                client_socket,addr = self.server_socket.accept()
                start_new_thread(self.threaded,(client_socket,addr))
            except:
                break
        self.server_socket.close()
        print("server closed...")
    def threaded(self,client_socket,addr):
        print("connected by:",addr[0],':',addr[1])
        stop = [False]
        name = addr[0]+":"+str(addr[1])
        th = Thread(target = self.sendresult,args=(client_socket,name,stop,))
        th.start()
        data_buffer = ""
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    print(name,"broken")
                    break
                data = data.decode('utf-8')
                data_buffer = data_buffer + data
                try:
                    if data_buffer.index('$'):
                        commands = data_buffer.split('$')[:-1]
                        data_buffer = data_buffer.split('$')[-1]
                        for command in commands:
                            command = command.split('%')
                            if len(command) == 1:
                                if command[0] == "result":
                                    buffer = ""
                                    for device in list(self.data.keys()):
                                        buffer = buffer + str(self.data[device]['result'][name])
                                        self.data[device]['result'][name] = []
                                    client_socket.send((buffer+'$').encode('utf-8'))
                                    
                                elif command[0] == "listen":
                                    buffer = ""
                                    for device in list(self.data.keys()):
                                        temp = self.data[device]['listen_result']
                                        buffer = buffer + device + '\t'
                                        for c in temp:
                                            if c == "":
                                                continue
                                            buffer = buffer + c + '\t'
                                        buffer = buffer[:-1] +'\t'+ self.data[device]['port'] + '\n'
                                    client_socket.send((buffer+'$').encode('utf-8'))
                                else:
                                    print("received wrongtype "+command[0])
                                    client_socket.send(("command error:"+command[0]+"$").encode('utf-8'))
                            else:
                                print(command)
                                device  = command[0]
                                for c in command[1:]:
                                    c = c + '%' + name
                                    self.data[device]['command'].append(c)
                            time.sleep(0.1)
                except:
                    pass
            except ConnectionResetError as e:
                break
        stop[0] = True
        th.join()
        for device in list(self.data.keys()):
            try:
                self.data[device]['result'][name].pop()
            except:
                pass
        client_socket.close()
        print("disconnected by"+addr[0],':',addr[1])
    def sendresult(self,client_socket,name,stop):
        for device in list(self.data.keys()):
            self.data[device]['result'][name] = []
        while stop[0] == False:
            for device in list(self.data.keys()):
                #try:
                result = self.data[device]['result'][name]
                if result != []:
                    print(name,result)
                    for send_file in result:
                        client_socket.send((device+'%'+send_file[0]+"$").encode('utf-8'))
                #except:
                    #pass
                self.data[device]['result'][name] = []
            time.sleep(1)

