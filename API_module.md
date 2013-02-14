Setting Commands Module
=======================

Properies (get):
- serno
- name
- code
- info1
- info2
- hw_version
- fw_version

Propertis (get, set)
- measure_mode
- measure_mode_waittime
- measure_mode_speeptime
- analog_mode
- moist_min
- moist_max
- temp_min
- temp_max

Functional commands
===================

measure_start()
measure_data()

read_eeprom()
write_eeprom(image)

Privat commands
================
def _unlock(self):

def _get_table(self, table):
def _set_table(self, table, data):

def _get_event_mode(self):
def _set_event_mode(self, mode="NormalMeasure"):


Support Module commands
=======================
Properies (get, set):
- serno
- name
- code
- info1
- info2
- hw_version
- sw_version

def set_analog_moist(self, mvolt=500):
def set_analog_temp(self, mvolt=500):

def turn_asic_on(self):
def turn_asic_off(self):

def get_transit_time_tdr(self):