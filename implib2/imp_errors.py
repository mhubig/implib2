#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Copyright (C) 2011-2012, Markus Hubig <mhubig@imko.de>

This file is part of IMPLib2 a small Python library implementing
the IMPBUS-2 data transmission protocol.

IMPLib2 is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

IMPLib2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with IMPLib2. If not, see <http://www.gnu.org/licenses/>.
"""

imp_error_classes = {
    1: 'Serial communication errors',
    2: 'Command errors',
    3: 'EEPROM errors',
    4: 'Others',
    5: 'TDR measuring errors',
    6: 'ADC, DAC, material temperature',
    7: 'Calculate errors',
    8: ' SelfTest errors',
    9: 'Reserverd error codes',
   10: 'More data waiting',
}

imp_errors = {
    # Serial communication errors
    1: (1, 'received address block invalid first byte should be 253'),
    2: (1, 'received address block check CRC'),
    3: (1, 'received data block check CRC'),
    4: (1, 'time out of receiving data block'),
    5: (1, 'V24'),
    6: (1, 'UART'),
    7: (1, 'time out of transmitting address block'),
    8: (1, 'time out of transmitting data block'),

    # Command errors
    20: (2, 'no command'),
    21: (2, 'parameter number isn’t in table'),
    22: (2, 'get page parameter'),
    23: (2, 'set page parameter'),
    24: (2, 'parameter is not writable'),
    25: (2, 'TDR scan parameter'),
    26: (2, 'have no support right'),
    27: (2, 'setting all parameters needs support right'),
    28: (2, 'the event of TDRScan must be set in advance'),
    29: (2, 'baud rate is too small'),
    30: (2, 'baud rate is too big'),

    # EEPROM errors
    41: (3, 'no response from EEPROM'),
    42: (3, 'page writing is out of range'),
    43: (3, 'SCL stuck to low'),
    44: (3, 'SDA stuck to low'),
    45: (3, 'write memory address'),
    46: (3, 'write data to EEPROM'),
    47: (3, 'get & set image parameter'),
    48: (3, 'ASIC errors'),
    49: (3, 'ASIC check is failed'),

    # Others
    60: (4, 'Voltage too low'),

    # TDR measuring errors
    100: (5, 'TDR position is over flow'),
    101: (5, 'TDR position is under flow'),
    102: (5, 'get ASIC temperature'),
    103: (5, 'EC divisor is zero'),
    105: (5, 'Tp is out of range'),
    106: (5, 'Resister is out of range'),
    108: (5, 'No reflect point is found'),

    # ADC, DAC, material temperature
    120: (6, 'A/D convert'),
    121: (6, 'D/A convert'),
    122: (6, 'get material temperature'),
    123: (6, 'get material temperature'),

    # Calculate errors
    130: (7, 'minimal or maximal gain threshold in calculating coefficients'),
    131: (7, 'divisor is zero in ASIC temperature compensation'),
    132: (7, 'actual moisture is too large in DAC'),
    133: (7, 'actual moisture is too small in DAC'),
    134: (7, 'actual temperature is too large in DAC'),
    135: (7, 'actual temperature is too small in DAC'),
    136: (7, 'TpMDivisor is zero'),
    137: (7, 'T to Ms mode is out of range'),
    138: (7, 'Ratio divisor is zero'),

    # SelfTest errors
    150: (8, 'DAC code is too small'),
    151: (8, 'DAC code is too large'),

    # Reserverd
    200: (9, 'reserved'),
    201: (9, 'reserved'),
    202: (9, 'reserved'),
    203: (9, 'reserved'),
    204: (9, 'reserved'),
    205: (9, 'reserved'),
    206: (9, 'reserved'),
    207: (9, 'reserved'),
    208: (9, 'reserved'),
    209: (9, 'reserved'),
    210: (9, 'reserved'),
    211: (9, 'reserved'),
    212: (9, 'reserved'),
    213: (9, 'reserved'),
    214: (9, 'reserved'),
    215: (9, 'reserved'),
    216: (9, 'reserved'),
    217: (9, 'reserved'),
    218: (9, 'reserved'),
    219: (9, 'reserved'),
    220: (9, 'reserved'),
    221: (9, 'reserved'),
    222: (9, 'reserved'),
    223: (9, 'reserved'),
    224: (9, 'reserved'),
    225: (9, 'reserved'),
    226: (9, 'reserved'),
    227: (9, 'reserved'),
    228: (9, 'reserved'),
    229: (9, 'reserved'),
    230: (9, 'reserved'),
    231: (9, 'reserved'),
    232: (9, 'reserved'),
    233: (9, 'reserved'),
    234: (9, 'reserved'),
    235: (9, 'reserved'),
    236: (9, 'reserved'),
    237: (9, 'reserved'),
    238: (9, 'reserved'),
    239: (9, 'reserved'),
    240: (9, 'reserved'),
    241: (9, 'reserved'),
    242: (9, 'reserved'),
    243: (9, 'reserved'),
    244: (9, 'reserved'),
    245: (9, 'reserved'),
    246: (9, 'reserved'),
    247: (9, 'reserved'),
    248: (9, 'reserved'),
    249: (9, 'reserved'),
    250: (9, 'reserved'),
    251: (9, 'reserved'),
    252: (9, 'reserved'),
    253: (9, 'reserved'),
    254: (9, 'reserved'),

    # More data waiting
    255: (10, 'more data'),
}

