Setting Commands Module
=======================

#### Properies (get)
* `serno` ✔
* `name` ✔
* `code` ✔
* `info1` ✔
* `info2` ✔
* `hw_version` ✔
* `fw_version` ✔

#### Propertis (get, set)
* `waittime` ✔
* `sleeptime` ✔
* `moist_range` ✔
* `temp_range` ✔

#### Functional commands
* `analog_mode` ✔
* `measure_mode(mode, param)` ✔
* `measure_start()` ✔
* `measure_running()`✔
* `measure_data()` ✔

* `read_eeprom()`
* `write_eeprom(image)`

#### Privat properties
* `_event_mode()` ✔

#### Private commands
* `_unlock()`

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

