Setting Commands Module
=======================

#### Properies (get)
* `serno`
* `name`
* `code`
* `info1`
* `info2`
* `hw_version`
* `fw_version`

#### Propertis (get, set)
* `measure_mode`
* `measure_mode_waittime`
* `measure_mode_speeptime`
* `analog_mode`
* `moist_min`
* `moist_max`
* `temp_min`
* `temp_max`

#### Functional commands
* `measure_start()`
* `measure_data()`
* `read_eeprom()`
* `write_eeprom(image)`

#### Privat commands
* `_unlock()`
* `_get_table()`
* `_set_table()`
* `_get_event_mode()`
* `_set_event_mode()`

Support Module commands
=======================

#### Properies (get, set)
* `serno`
* `name`
* `code`
* `info1`
* `info2`
* `hw_version`
* `fw_version`

#### Functional commands
* `set_analog_moist()`
* `set_analog_temp()`
* `turn_asic_on()`
* `turn_asic_off()`
* `get_transit_time_tdr()`

