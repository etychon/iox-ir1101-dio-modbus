from pymodbus.client.sync import ModbusTcpClient
#import logging
import time
import random

#FORMAT = ('%(asctime)-15s %(threadName)-15s '
#          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
#logging.basicConfig(format=FORMAT)
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)

UNIT = 0x1

while True:
    
    client = ModbusTcpClient("192.168.2.101", port=5020)
    #client = ModbusTcpClient("192.168.2.6", port=5020)
    client.connect()

    for x in range(4):

        #try:
            r = int(random.getrandbits(1))                                                                                                                                                                     
            result = client.write_coil(x, r, unit=UNIT)
        #except:
        #    print("Server not running.")
        #    break
        #else:
        #    print(str(x) + ": " + str(result))
    
    client.close()

    print("------")

    time.sleep(2);
