#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import numpy as np
import logging
import implib2

logging.basicConfig(
        format='%(message)s',
        filename='scan.log',
        level=logging.DEBUG)

bus = implib2.Bus('/dev/ttyUSB0')

def scan(trans_wait, cycle_wait, range_wait):
    bus.trans_wait = trans_wait
    bus.cycle_wait = cycle_wait
    bus.range_wait = range_wait

    try:
        tic = time.time()
        probes = bus.scan_bus()
        s_time = time.time() - tic
    except implib2.BusError as err:
        logging.debug('ERROR: %s', err)
        probes = []
        s_time = 0.0
    finally:
        time.sleep(0.1)

    return len(probes), s_time, probes

reference = set([10000, 10001, 10002, 10003, 10004,
    10005, 10006, 10007, 10008, 10009, 10010, 10011])

serie = 0

logging.debug("serie;nr;found;time;pause;timeout;probes")
for trans_wait in np.arange(0.070, 0.075, 0.005):
    for cycle_wait in np.arange(0.070, 0.075, 0.005):
        for range_wait in np.arange(0.070, 0.075, 0.005):
            serie += 1

            bus.dev.open_device()
            bus.wakeup()
            bus.synchronise_bus()

            for nr in range(1,11):
                print "== Serie: {} == Nr: {} =================================".format(serie, nr)
                found, s_time, probes = scan(trans_wait, cycle_wait, range_wait)
                probes = list(reference - set(probes))
                msg = "{:03};{:02};{:02};{:.6f};{:.3f};{:.3f};{:.3f};{}".format(serie, nr, found,
                        s_time, trans_wait, cycle_wait,range_wait, probes)
                logging.debug()

            bus.dev.close_device()

