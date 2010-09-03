#!/usr/bin/python
# -*- coding: UTF-8 -*-

# TODO: Invent some nice general error handling
#

import binascii, time, sys
import threading, thread, Queue

from bluetooth import *
from select import *
from crc import CRC
from timeout import Timeout

def find(devname):
    """ Discovers a BT device of name 'devname' and saves its HW-Address.
    with the use of this HW-Address it finds the port offering a IMPBUS
    Service """
    
    host = None
    port = None
    queue = Queue.Queue()

    try:
        t = Timeout( queue, 30 ).start()

        while not host:
            # getting the address
            nearby = discover_devices(duration=8, flush_cache=True, lookup_names=True)
            for addr, name in nearby:
                if name == devname:
                    host = addr
    
        while not port:
            # getting the avalible protocol for IMPBUS
            service = find_service( name = 'IMPBUS', address = host )
            for srv in service:
                if srv["protocol"] == "RFCOMM":
                    port = srv["port"]
        
        queue.put('exit')
        return host, port
    
    except:
        sys.exit()

def write(str, socket):
    """ select waits for the socket to get into writeable state
    then sends the converted binary sting """

    while True:
        readable, writeable, excepts = select( [], [socket], [], 1 )
        if socket in writeable:
            time.sleep(0.5)
            print "sending command:     ", str
            socket.send( binascii.a2b_hex(str) )
            break

def read(socket):
    """ select waits for the socket to get into readable state
    then reads up to 260 (253 daten + 7 header) bytes """
    
    while True:
        readable, writeable, excepts = select( [socket], [], [], 1 )
        if socket in readable:
            time.sleep(0.5)
            res = binascii.b2a_hex( socket.recv(260) )
            print "response from sensor:", res
            break
    
    return res

def cut_data(str):
    """ Data is starting at byte 7 that is char 14 of my ASCII HEX string.
    The langth of the DATA part is coded at byte 2 that is char 4 & 5
    of my ASCII HEX string """

    data_start  = 14
    data_length = 2 * int(str[4:6], 16)
    data_end    = data_start + data_length
    data_all    = str[data_start:data_end]

    if crc.check(data_all):
        data = data_all[:-2]
        return data
    else:
        return None

def get_serno(str):
    data = cut_data(str)
    data = data[4:6]+data[2:4]+data[0:2]
    print "Data:", data
    return int(data, 16)

def main(argv):

    DEVNAME = "PICO-BT 0053"

    str_find    = 'FD0800FFFFFF60'
    str_measure = 'FD1504397700100600018F'
    str_ready   = 'FD14033977005B0600AA'
    str_getdata = 'FD1603397700D8FF0081'

    socket = BluetoothSocket( RFCOMM )
    socket.setblocking( False )

    host, port = find(DEVNAME)

    try: socket.connect( ( host, port ) )
    except: pass
    finally:
        print "Connectet to %s on Port %s" %(host,port) 
    
    write( str_find, socket )
    result = read( socket )
    serno = get_serno(result)
    print "Seriennummer:", serno

    write( str_measure, socket )
    result = read( socket )

    if result == "00150039770026":

        print "OK. Measure started ..."

        while True:
            write( str_ready, socket )
            reply = read( socket )
            data  = cut_data( reply )

            if data == '00':
                print "Ready? -> Yes!"
                break
            elif data == '01':
                print "Ready? -> No!"

        write( str_getdata, socket )
        reply = read( socket )
        data  = cut_data( reply )

        print data

#TODO: Print some real results
#
#       print
#       print "============================="
#       print "MeasureCount:"
#       print "Hex:", binascii.b2a_hex(data_h[0:4])
#       print "Dec:", struct.unpack('>f',data_h[3]+data_h[2]+data_h[1]+data_h[0])[0]
#       print "============================="
#       print "ASICTemperatur:"
#       print "Hex:", binascii.b2a_hex(data_h[12:16])
#       print "Dec:", struct.unpack('>f',data_h[15]+data_h[14]+data_h[13]+data_h[12])[0]
#       print "============================="
#       print "MatMoist:"
#       print "Hex:", binascii.b2a_hex(data_h[28:32])
#       print "Dec:", struct.unpack('>f',data_h[31]+data_h[30]+data_h[29]+data_h[28])[0]
#       print "============================="
#       print

    socket.close()

if __name__ == "__main__":
    crc = CRC()
    main(sys.argv[1:])

## <<EOF>>
