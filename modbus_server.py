#!/usr/bin/env python
"""
Pymodbus TCP Server With Callbacks and Cisco IR1101 Digital I/O polling
--------------------------------------------------------------------------
"""
# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

# --------------------------------------------------------------------------- #
# import the python libraries we need
# --------------------------------------------------------------------------- #
from multiprocessing import Queue, Process
import random

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------- #
# create your custom data block with callbacks
# --------------------------------------------------------------------------- #

class CallbackDataBlock(ModbusSparseDataBlock):
    """ A datablock that stores the new value in memory
    and passes the operation to a message queue for further
    processing.
    """

    def __init__(self, devices, queue):
        self.devices = devices
        self.queue = queue

        values = {k: 0 for k in devices.keys()}
        values[0xbeef] = len(values)  # the number of devices
        super(CallbackDataBlock, self).__init__(values)

    def setValues(self, address, value):
        """ Sets the requested values of the datastore

        :param address: The starting address - in this case the DIO port
        :param values: The new values to be set
        """
        super(CallbackDataBlock, self).setValues(address, value)
        self.queue.put((self.devices.get(address, None), value))

    def getValues(self, address, count=1):
        """ Gets the actual Digital I/O port values 
        
        :param address: The starting address - in this case the DIO port
        :param count: The number values to be get - 1 in this case
        """
         
        device = self.devices.get(address, None)
        try:
            # Let's do the actual read on that DIO port
            with open(str(device), "r") as c:
                c_read = int(c.read()[0])
                log.debug("*** Read(%s) = %s" % (device, c_read))
                c.close()
        except:
            import traceback
            traceback.print_exc()
            c_read = None
        return [c_read]

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #


def device_writer(queue):
    """ A worker process that processes new messages
    from a queue to write to device outputs

    :param queue: The queue to get new messages from
    """

    while True:
        device, value = queue.get()
        value = int(value[0]) # Convert Bool to int
        log.debug("*** Write(%s) = %s" % (device, value))
        if not device:
            log.debug("Device %s not found, continue" % (device))
            continue
        # Let's do the actual write on the DIO port
        try:
            with open(str(device), "w") as c:
                c.write(str(value)+"\n")
                c.flush()
                c.close()
        except:
            import traceback
            traceback.print_exc()
            continue

# --------------------------------------------------------------------------- #
# initialize your device map
# --------------------------------------------------------------------------- #


def read_device_map():
    """ A helper method to read the device
    path to address mapping. For IR1101 we will use 
    a static mapping like so:

       0x0001,/dev/dio-1
       0x0002,/dev/dio-2 
       0x0001,/dev/dio-3
       0x0002,/dev/dio-4                

    :returns: The input mapping file
    """
    devices = {1: '/dev/dio-1', 
               2: '/dev/dio-2', 
               3: '/dev/dio-3', 
               4: '/dev/dio-4'}

    return devices


def run_callback_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #
    queue = Queue()
    devices = read_device_map()
    block = CallbackDataBlock(devices, queue)
    store = ModbusSlaveContext(di=None, co=block, hr=None, ir=None)
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Cisco'
    identity.ProductCode = 'IR1101'
    identity.VendorUrl = 'http://www.cisco.com/'
    identity.ProductName = 'Cisco IR1101'
    identity.ModelName = 'GPIO'
    identity.MajorMinorRevision = '2.3.0'

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    p = Process(target=device_writer, args=(queue,))
    p.start()
    StartTcpServer(context, identity=identity, address=("", 5020))


if __name__ == "__main__":
    run_callback_server()
