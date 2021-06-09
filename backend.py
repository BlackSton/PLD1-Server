from time import sleep
import os
import sys
import listen
import server_socket

if __name__ == "__main__": 
    data = {"temp"    : {"port":"","listencommand":[],'listen_result':[],'command':[],'result':{},'fault':0},
             "vaccum" : {"port":"","listencommand":[],'listen_result':[],'command':[],'result':{},'fault':0},
             "laser"  : {"port":"","listencommand":[],'listen_result':[],'command':[],'result':{},'fault':0},
             "stepper": {"port":"","listencommand":[],'listen_result':[],'command':[],'result':{},'fault':0},}
    serial = listen.Serial(data)
    serial.listen()
    server = server_socket.tcp(data)
    try:
        while True:
            #os.system("clear")
            #"\033[95m"
            #print("Device\t\tConnection")
            #print("Temperature\t"+data["temp"]["port"])
            #print("Vaccum\t\t"+data["vaccum"]["port"])
            #print("LASER\t\t"+data["laser"]["port"])
            #print("Stepper\t\t"+data["stepper"]["port"])
            #print(data)
            sleep(0.5)
    except KeyboardInterrupt:
        serial.off()
        server.close = True
        sys.exit()