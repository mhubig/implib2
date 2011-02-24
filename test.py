from bus_interface import IMPBus
from module_interface import Module
bus = IMPBus('/dev/tty.usbserial-A700eQFp')
bus.DEBUG = True
 
modules = bus.scan_bus()
module = modules[0]
