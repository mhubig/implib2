#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2009-2012, Markus Hubig <mhubig@imko.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from packet import Packet,PacketError

class BaseCommandsError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class BaseCommands(Packet):
    """ COMMANDS TO CONTROL BUS.
    
    After building-up a IMP232N-bus, it is necessary for the master to find
    out, which slaves are connected to the bus. This class provides the needed
    low level commands like get_long_acknowledge, get_short_acknowledge and
    get_negative_acknowledge.
    
    COMMANDS TO CONTROL BUS AND TRANSFER PARAMETERS
    
    The main commands to transfer parameters are Get and Set Parameters.
    Get Parameters means information transport from slave to master and
    Set Parameters from master to slave.
    The parameters are divided in groups. There are different command
    numbers to get or set the parameters of a parameter group.
    
    +--------------------------+------------------+-------------------+
    | Parameter group:         |     Examples     |     Command no.   |
    |                          |                  |   Get   |   Set   |
    +--------------------------+------------------+---------+---------+
    | System parameters        | Baud rate        |   10    |   11    |
    +--------------------------+------------------+---------+---------+
    | Device configuration     | Measure cycle,   |   12    |   13    |
    | parameters               | Measurement rate |         |         |
    +--------------------------+------------------+---------+---------+
    | Device calibration       | ASIC TC,         |   14    |   15    |
    | parameters               | Electronic offset|         |         |
    +--------------------------+------------------+---------+---------+
    | Probe configuration      | TDR measure      |   16    |   17    |
    | prameters                | parameters       |         |         |
    +--------------------------+------------------+---------+---------+
    | Probe calibration        | Basic balancing, |   18    |   19    |
    | parameters               | Temp compensation|         |         |
    +--------------------------+------------------+---------+---------+
    | Action parameters        | SysErr, Event    |   20    |   21    |
    +--------------------------+------------------+---------+---------+
    | Measure parameters       | Count,t,tp,Ms    |   22    |   23    |
    +--------------------------+------------------+---------+---------+
    | Tp Moist parameters      | 101 points for   |   24    |   25    |
    |                          | calculating moist|         |         |
    +--------------------------+------------------+---------+---------+
    
    The parameters to be transferred by get or set commands are identified
    by a number, which is sent within the data block. There are special
    parameter as follows:  
    
    +----------------+------------------------------------------------+
    | Parameter no.: | Explanation:                                   |
    +----------------+------------------------------------------------+
    | 0x01 ... 0xFA  | Ordinary number of the parameter to set or get |
    +----------------+------------------------------------------------+
    | 0xFB           | Configuration identification                   |
    +----------------+------------------------------------------------+
    | 0xFC           | The size of the parameter table                |
    +----------------+------------------------------------------------+
    | 0xFD           | Parameter table, infos about parameter group   |
    +----------------+------------------------------------------------+
    | 0xFE           | The data length of the parameter group         |
    +----------------+------------------------------------------------+
    | 0xFF           | Get all parameters of the parameter group      |
    +----------------+------------------------------------------------+
    
    For more details please refer to the "Developers Manual, Data Transmission
    Protocol for IMPBUS2, 2008-11-18".
    """
    def __init__(self):
        Packet.__init__(self)
        
        self.SYSTEM_PARAMETER_TABLE = {
            'Table': {'Name': 'SYSTEM_PARAMETER_TABLE', 'Get': 10, 'Set': 11},
            'SerialNum':   {'No':0x01, 'Type':0x04, 'Status':'WR', 'Length':4},
            'HWVersion':   {'No':0x02, 'Type':0x06, 'Status':'OR', 'Length':4},
            'FWVersion':   {'No':0x03, 'Type':0x06, 'Status':'OR', 'Length':4},
            'Baudrate':    {'No':0x04, 'Type':0x02, 'Status':'WR', 'Length':2},
            'ModuleName':  {'No':0x05, 'Type':0x80, 'Status':'OR', 'Length':16},
            'ModuleCode':  {'No':0x06, 'Type':0x02, 'Status':'OR', 'Length':2},
            'ModuleInfo1': {'No':0x07, 'Type':0x00, 'Status':'WR', 'Length':1},
            'ModuleInfo2': {'No':0x08, 'Type':0x00, 'Status':'WR', 'Length':1},
            'ConfigID':    {'No':0xfb, 'Type':0x02, 'Status':'OR', 'Length':2}}
        
        self.DEVICE_CONFIGURATION_PARAMETER_TABLE = {
            'Table': {'Name': 'DEVICE_CONFIGURATION_PARAMETER_TABLE', 'Get': 12, 'Set': 13},
            'MeasMode':         {'No':0x01, 'Type':0x00, 'Status':'WR', 'Length':1},
            'MeasTimes':        {'No':0x02, 'Type':0x00, 'Status':'WR', 'Length':1},
            'SleepTimeInModeC': {'No':0x03, 'Type':0x04, 'Status':'WR', 'Length':4},
            'WaitTimeInModeB':  {'No':0x04, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MoistMaxValue':    {'No':0x05, 'Type':0x00, 'Status':'WR', 'Length':1},
            'MoistMinValue':    {'No':0x06, 'Type':0x00, 'Status':'WR', 'Length':1},
            'TempMaxValue':     {'No':0x07, 'Type':0x01, 'Status':'WR', 'Length':1},
            'TempMinValue':     {'No':0x08, 'Type':0x01, 'Status':'WR', 'Length':1},
            'MoistAnalogAdjust':{'No':0x09, 'Type':0x00, 'Status':'WR', 'Length':1},
            'TempAnalogAdjust': {'No':0x0a, 'Type':0x00, 'Status':'WR', 'Length':1},
            'TMsMode':          {'No':0x0b, 'Type':0x02, 'Status':'WR', 'Length':2},
            'EPRByteLen':       {'No':0x0c, 'Type':0x02, 'Status':'OR', 'Length':2},
            'ConfigID':         {'No':0xfb, 'Type':0x02, 'Status':'OR', 'Length':2}}
            
        self.DEVICE_CALIBRATION_PARAMETER_TABLE = {
            'Table': {'Name': 'DEVICE_CALIBRATION_PARAMETER_TABLE', 'Get': 14, 'Set': 15},
            'ASICTempCorr':    {'No':0x01, 'Type':0x86, 'Status':'OR', 'Length':24},
            'ASICTCStartTemp': {'No':0x02, 'Type':0x01, 'Status':'OR', 'Length':1},
            'ASICTCHeatTemp':  {'No':0x03, 'Type':0x00, 'Status':'OR', 'Length':1},
            'ASICTCEndTemp':   {'No':0x04, 'Type':0x00, 'Status':'OR', 'Length':1},
            'ASICTCSpanTemp':  {'No':0x05, 'Type':0x00, 'Status':'OR', 'Length':1},
            'ECZeroOffset':    {'No':0x06, 'Type':0x06, 'Status':'OR', 'Length':4},
            'ECDivisor':       {'No':0x07, 'Type':0x06, 'Status':'OR', 'Length':4},
            'ConfigID':        {'No':0xfb, 'Type':0x02, 'Status':'OR', 'Length':2}}
            
        self.PROBE_CONFIGURATION_PARAMETER_TABLE = {
            'Table': {'Name': 'PROBE_CONFIGURATION_PARAMETER_TABLE', 'Get': 16, 'Set': 17},
            'SearchGradient':      {'No':0x01, 'Type':0x02, 'Status':'OR', 'Length':2},
            'StartThreshold':      {'No':0x02, 'Type':0x00, 'Status':'OR', 'Length':1},
            'GradHighLowDistance': {'No':0x03, 'Type':0x00, 'Status':'OR', 'Length':1},
            'StartMoveDistance':   {'No':0x04, 'Type':0x00, 'Status':'OR', 'Length':1},
            'StepDown':            {'No':0x05, 'Type':0x00, 'Status':'OR', 'Length':1},
            'Timeout':             {'No':0x06, 'Type':0x02, 'Status':'OR', 'Length':2},
            'ASICWarmPulse':       {'No':0x07, 'Type':0x02, 'Status':'OR', 'Length':2},
            'MinValidTp':          {'No':0x08, 'Type':0x06, 'Status':'WR', 'Length':4},
            'MaxValidTp':          {'No':0x09, 'Type':0x06, 'Status':'WR', 'Length':4},
            'ProbeType':           {'No':0x0a, 'Type':0x00, 'Status':'OR', 'Length':1},
            'ProbeNo':             {'No':0x0b, 'Type':0x00, 'Status':'WR', 'Length':1},
            'DeviceSerialNum':     {'No':0x0c, 'Type':0x04, 'Status':'WR', 'Length':4},
            'TempSensorCoeff':     {'No':0x0d, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TempSensorADCode':    {'No':0x0e, 'Type':0x82, 'Status':'WR', 'Length':12},
            'ConfigID':            {'No':0xfb, 'Type':0x02, 'Status':'OR', 'Length':2}}
         
        self.PROBE_CALIBRATION_PARAMETER_TABLE = {
            'Table': {'Name': 'PROBE_CALIBRATION_PARAMETER_TABLE', 'Get': 18, 'Set': 19},
            'BasicCoeff':     {'No':0x01, 'Type':0x86, 'Status':'WR', 'Length':24}, 
            'StdCoeff':       {'No':0x02, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DefaultCalItem': {'No':0x03, 'Type':0x00, 'Status':'WR', 'Length':1},
            'Reserved':       {'No':0x04, 'Type':0x00, 'Status':'WR', 'Length':1},
            
            'CalID0':         {'No':0x05, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName0':       {'No':0x06, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID0':         {'No':0x07, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff0':      {'No':0x08, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID0':         {'No':0x09, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff0':      {'No':0x0a, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID0':         {'No':0x0b, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff0':      {'No':0x0c, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID1':         {'No':0x0d, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName1':       {'No':0x0e, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID1':         {'No':0x0f, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff1':      {'No':0x10, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID1':         {'No':0x11, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff1':      {'No':0x12, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID1':         {'No':0x13, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff1':      {'No':0x14, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID2':         {'No':0x15, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName2':       {'No':0x16, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID2':         {'No':0x17, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff2':      {'No':0x18, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID2':         {'No':0x19, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff2':      {'No':0x1a, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID2':         {'No':0x1b, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff2':      {'No':0x1c, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID3':         {'No':0x1d, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName3':       {'No':0x1f, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID3':         {'No':0x20, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff3':      {'No':0x21, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID3':         {'No':0x22, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff3':      {'No':0x23, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID3':         {'No':0x24, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff3':      {'No':0x25, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID4':         {'No':0x26, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName4':       {'No':0x27, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID4':         {'No':0x28, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff4':      {'No':0x29, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID4':         {'No':0x2a, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff4':      {'No':0x2b, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID4':         {'No':0x2c, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff4':      {'No':0x2d, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID5':         {'No':0x2e, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName5':       {'No':0x2f, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID5':         {'No':0x30, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff5':      {'No':0x31, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID5':         {'No':0x32, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff5':      {'No':0x33, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID5':         {'No':0x34, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff5':      {'No':0x35, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID6':         {'No':0x36, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName6':       {'No':0x37, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID6':         {'No':0x38, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff6':      {'No':0x39, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID6':         {'No':0x3a, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff6':      {'No':0x3b, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID6':         {'No':0x3c, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff6':      {'No':0x3d, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID7':         {'No':0x3e, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName7':       {'No':0x3f, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID7':         {'No':0x40, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff7':      {'No':0x41, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID7':         {'No':0x41, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff7':      {'No':0x42, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID7':         {'No':0x43, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff7':      {'No':0x44, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID8':         {'No':0x45, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName8':       {'No':0x46, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID8':         {'No':0x47, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff8':      {'No':0x48, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID8':         {'No':0x49, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff8':      {'No':0x4a, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID8':         {'No':0x4b, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff8':      {'No':0x4c, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID9':         {'No':0x4d, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName9':       {'No':0x4e, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID9':         {'No':0x4f, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff9':      {'No':0x50, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID9':         {'No':0x51, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff9':      {'No':0x52, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID9':         {'No':0x53, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff9':      {'No':0x54, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID10':        {'No':0x55, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName10':      {'No':0x56, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID10':        {'No':0x57, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff10':     {'No':0x58, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID10':        {'No':0x59, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff10':     {'No':0x5a, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID10':        {'No':0x5b, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff10':     {'No':0x5c, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID11':        {'No':0x5d, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName11':      {'No':0x5e, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID11':        {'No':0x5f, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff11':     {'No':0x60, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID11':        {'No':0x61, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff11':     {'No':0x62, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID11':        {'No':0x63, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff11':     {'No':0x64, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID12':        {'No':0x65, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName12':      {'No':0x66, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID12':        {'No':0x67, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff12':     {'No':0x68, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID12':        {'No':0x69, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff12':     {'No':0x6a, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID12':        {'No':0x6b, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff12':     {'No':0x6c, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID13':        {'No':0x6d, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName13':      {'No':0x6e, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID13':        {'No':0x6f, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff13':     {'No':0x70, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID13':        {'No':0x71, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff13':     {'No':0x72, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID13':        {'No':0x73, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff13':     {'No':0x74, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID14':        {'No':0x75, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName14':      {'No':0x76, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID14':        {'No':0x77, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff14':     {'No':0x78, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID14':        {'No':0x79, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff14':     {'No':0x7a, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID14':        {'No':0x7b, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff14':     {'No':0x7c, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'CalID15':        {'No':0x7d, 'Type':0x02, 'Status':'WR', 'Length':2},
            'CalName15':      {'No':0x7e, 'Type':0x80, 'Status':'WR', 'Length':32},
            'MatID15':        {'No':0x7f, 'Type':0x02, 'Status':'WR', 'Length':2},
            'MatCoeff15':     {'No':0x80, 'Type':0x86, 'Status':'WR', 'Length':24},
            'TemID15':        {'No':0x81, 'Type':0x02, 'Status':'WR', 'Length':2},
            'TemCoeff15':     {'No':0x82, 'Type':0x86, 'Status':'WR', 'Length':24},
            'DenID15':        {'No':0x83, 'Type':0x02, 'Status':'WR', 'Length':2},
            'DenCoeff15':     {'No':0x84, 'Type':0x85, 'Status':'WR', 'Length':24},
            
            'ConfigID':       {'No':0xfb, 'Type':0x02, 'Status':'OR', 'Length':2}}
            
        self.ACTION_PARAMETER_TABLE = {
            'Table': {'Name': 'ACTION_PARAMETER_TABLE', 'Get': 20, 'Set': 21},
            'SysErr':       {'No':0x01, 'Type':0x00, 'Status':'OR', 'Length':1},
            'AppErr':       {'No':0x02, 'Type':0x00, 'Status':'OR', 'Length':1},
            'Event':        {'No':0x03, 'Type':0x00, 'Status':'WR', 'Length':1},
            'DoASICTC':     {'No':0x04, 'Type':0x00, 'Status':'WR', 'Length':1},
            'EnterSleep':   {'No':0x05, 'Type':0x00, 'Status':'WR', 'Length':1},
            'StartMeasure': {'No':0x06, 'Type':0x00, 'Status':'WR', 'Length':1},
            'ActCalItem':   {'No':0x07, 'Type':0x00, 'Status':'WR', 'Length':1},
            'Reserved':     {'No':0x08, 'Type':0x00, 'Status':'WR', 'Length':1},
            'SupportPW':    {'No':0x09, 'Type':0x02, 'Status':'WR', 'Length':1},
            'PowerVolt':    {'No':0x0a, 'Type':0x06, 'Status':'WR', 'Length':1},
            'SelfTest':     {'No':0x0b, 'Type':0x80, 'Status':'OR', 'Length':1}}
        
        self.MEASURE_PARAMETER_TABLE = {
            'Table': {'Name': 'MEASURE_PARAMETER_TABLE', 'Get': 22, 'Set': 23},
            'MeasureCount':      {'No':0x01, 'Type':0x04, 'Status':'OR', 'Length':4},
            'CalcucCount':       {'No':0x02, 'Type':0x06, 'Status':'OR', 'Length':4},
            'CountWithASICTC':   {'No':0x03, 'Type':0x06, 'Status':'OR', 'Length':4},
            'ASICTemperature':   {'No':0x04, 'Type':0x06, 'Status':'OR', 'Length':4},
            'TransitTime':       {'No':0x05, 'Type':0x06, 'Status':'OR', 'Length':4},
            'PseudoTransitTime': {'No':0x06, 'Type':0x06, 'Status':'OR', 'Length':4},
            'StdMoist':          {'No':0x07, 'Type':0x06, 'Status':'OR', 'Length':4},
            'MatMoist':          {'No':0x08, 'Type':0x06, 'Status':'OR', 'Length':4},
            'TempMoist':         {'No':0x09, 'Type':0x06, 'Status':'OR', 'Length':4},
            'Moist':             {'No':0x0a, 'Type':0x06, 'Status':'WR', 'Length':4},
            'TDRValue':          {'No':0x0b, 'Type':0x06, 'Status':'OR', 'Length':4},
            'MeasTemp':          {'No':0x0c, 'Type':0x06, 'Status':'WR', 'Length':4},
            'CompTemp':          {'No':0x0d, 'Type':0x06, 'Status':'WR', 'Length':4},
            'Density':           {'No':0x0e, 'Type':0x06, 'Status':'OR', 'Length':4},
            'Info1':             {'No':0x0f, 'Type':0x06, 'Status':'OR', 'Length':4},
            'Info2':             {'No':0x10, 'Type':0x06, 'Status':'OR', 'Length':4}}
        
        self.TP_MOIST_PARAMETER_TABLE = {
            'Table': {'Name': 'TP_MOIST_PARAMETER_TABLE', 'Get': 24, 'Set': 25},
            'Point0':   {'No':0x01, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point1':   {'No':0x02, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point2':   {'No':0x03, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point3':   {'No':0x04, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point4':   {'No':0x05, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point5':   {'No':0x06, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point6':   {'No':0x07, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point7':   {'No':0x08, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point8':   {'No':0x09, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point9':   {'No':0x0a, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point10':  {'No':0x0b, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point11':  {'No':0x0c, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point12':  {'No':0x0d, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point13':  {'No':0x0e, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point14':  {'No':0x0f, 'Type':0x86, 'Status':'WR', 'Length':8},
            
            'Point15':  {'No':0x10, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point16':  {'No':0x11, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point17':  {'No':0x12, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point18':  {'No':0x13, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point19':  {'No':0x14, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point20':  {'No':0x15, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point21':  {'No':0x16, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point22':  {'No':0x17, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point23':  {'No':0x18, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point24':  {'No':0x19, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point25':  {'No':0x1a, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point26':  {'No':0x1b, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point27':  {'No':0x1c, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point28':  {'No':0x1d, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point29':  {'No':0x1e, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point30':  {'No':0x1f, 'Type':0x86, 'Status':'WR', 'Length':8},
            
            'Point31':  {'No':0x20, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point32':  {'No':0x21, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point33':  {'No':0x22, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point34':  {'No':0x23, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point35':  {'No':0x24, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point36':  {'No':0x25, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point37':  {'No':0x26, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point38':  {'No':0x27, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point39':  {'No':0x28, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point40':  {'No':0x29, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point41':  {'No':0x2a, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point42':  {'No':0x2b, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point43':  {'No':0x2c, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point44':  {'No':0x2d, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point45':  {'No':0x2e, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point46':  {'No':0x2f, 'Type':0x86, 'Status':'WR', 'Length':8},
            
            'Point47':  {'No':0x30, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point48':  {'No':0x31, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point49':  {'No':0x32, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point50':  {'No':0x33, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point51':  {'No':0x34, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point52':  {'No':0x35, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point53':  {'No':0x36, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point54':  {'No':0x37, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point55':  {'No':0x38, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point56':  {'No':0x39, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point57':  {'No':0x3a, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point58':  {'No':0x3b, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point59':  {'No':0x3c, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point60':  {'No':0x3d, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point61':  {'No':0x3e, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point62':  {'No':0x3f, 'Type':0x86, 'Status':'WR', 'Length':8},
            
            'Point63':  {'No':0x40, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point64':  {'No':0x41, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point65':  {'No':0x42, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point66':  {'No':0x43, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point67':  {'No':0x44, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point68':  {'No':0x45, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point69':  {'No':0x46, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point70':  {'No':0x47, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point71':  {'No':0x48, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point72':  {'No':0x49, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point73':  {'No':0x4a, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point74':  {'No':0x4b, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point75':  {'No':0x4c, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point76':  {'No':0x4d, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point77':  {'No':0x4e, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point78':  {'No':0x4f, 'Type':0x86, 'Status':'WR', 'Length':8},
            
            'Point79':  {'No':0x50, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point80':  {'No':0x51, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point81':  {'No':0x52, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point82':  {'No':0x53, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point83':  {'No':0x54, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point84':  {'No':0x55, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point85':  {'No':0x56, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point86':  {'No':0x57, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point87':  {'No':0x58, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point88':  {'No':0x59, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point89':  {'No':0x5a, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point90':  {'No':0x5b, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point91':  {'No':0x5c, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point92':  {'No':0x5d, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point93':  {'No':0x5e, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point94':  {'No':0x5f, 'Type':0x86, 'Status':'WR', 'Length':8},
            
            'Point95':  {'No':0x60, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point96':  {'No':0x61, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point97':  {'No':0x62, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point98':  {'No':0x63, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point99':  {'No':0x64, 'Type':0x86, 'Status':'WR', 'Length':8},
            'Point100': {'No':0x65, 'Type':0x86, 'Status':'WR', 'Length':8},
            'ConfigID': {'No':0xfb, 'Type':0x02, 'Status':'OR', 'Length':2}}
        
        self.param_tables = [self.SYSTEM_PARAMETER_TABLE,
            self.DEVICE_CALIBRATION_PARAMETER_TABLE,
            self.PROBE_CONFIGURATION_PARAMETER_TABLE,
            self.PROBE_CALIBRATION_PARAMETER_TABLE,
            self.ACTION_PARAMETER_TABLE,
            self.MEASURE_PARAMETER_TABLE,
            self.TP_MOIST_PARAMETER_TABLE]
    
    def get_long_acknowledge(self,serno):
        """ Command to PING a specific module.
        
        This command with the number 2 will call up the slave which is
        addressed by its serial number. In return, the slave replies with
        a complete address block. It can be used to test the presence of
        a module in conjunction with the quality of the bus connection.
        
        >>> from basecommands import BaseCommands
        >>> import binascii
        >>> b = BaseCommands()
        >>> p = b.get_long_acknowledge(31001)
        >>> print binascii.b2a_hex(p)
        fd02001979007b
        """
        packet = self.pack(serno=serno,cmd=0x02)
        return packet
    
    def get_short_acknowledge(self,serno):
        """ GET SHORT ACKNOWLEDGE

        This command will call up the slave which is addressed by its serial
        number. In return, the slave replies by just one byte: The CRC of it's
        serial number. It is the shortest possible command without the transfer
        of any data block and the only one without a complete address block. It
        can be used to test the presence of a module.
        
        >>> from basecommands import BaseCommands
        >>> import binascii
        >>> b = BaseCommands()
        >>> p = b.get_short_acknowledge(31001)
        >>> print binascii.b2a_hex(p)
        fd0400197900e7
        """
        packet = self.pack(serno=serno,cmd=0x04)
        return packet
          
    def get_acknowledge_for_serial_number_range(self,range):
        """ GET ACKNOWLEDGE FOR SERIAL NUMBER RANGE

        This command is very similar to the get_short_acknowledge command.
        However, it addresses not just one single serial number, but a serial
        number range. This value of byte 4 to byte 6 symbolizes a whole range
        according to the following pattern:
        
        +-----------+-------------+----------+---------------------+
        | High byte | Medium byte | Low byte |       Range         |
        +-----------+-------------+----------+---------------------+
        | 01000000  | 00000000    | 00000000 | 0x000000 - 0x7FFFFF |
        +-----------+-------------+----------+---------------------+
        | 11000000  | 00000000    | 00000000 | 0x800000 - 0xFFFFFF |
        +-----------+-------------+----------+---------------------+
        | usw.      |             |          |                     |
        
        The lowest "1" is not a part of the value but the (right) mark where
        the relevant value ends. All bits left of this mark are relevant, all
        bits right of this mark are non-relevant, including the mark itself.
        
        All modules within thus indicated range are addressed and will
        respond. The master can just detect if there is no response, which
        means that there is no slave within this range, or if there is a
        response of one or more slaves. The range must then be halved more
        and more to refine the search.
        
        two examples:
        =============
        
        start range: 10000000 00000000 00000000
        shift mark:   1000000 00000000 00000000
        lower half:  01000000 00000000 00000000 (old mark gets 0)
        higher half: 11000000 00000000 00000000 (old mark gets 1)
        
        start range: 11100000 00000000 00000000
        shift mark:     10000 00000000 00000000
        lower half:  11010000 00000000 00000000 (old mark gets 0)
        higher half: 11110000 00000000 00000000 (old mark gets 1)
        
        >>> from basecommands import BaseCommands
        >>> import binascii
        >>> b = BaseCommands()
        >>> serno = int(0b111100000000000000000000)
        >>> p = b.get_acknowledge_for_serial_number_range(serno)
        >>> print binascii.b2a_hex(p)
        fd06000000f0d0
        """
        packet = self.pack(serno=range,cmd=0x06)
        return packet
    
    def get_negative_acknowledge(self):
        """ GET NEGATIVE ACKNOWLEDGE
        
        This command is used to identify a single module on the bus which
        serial number is unknown. It is a broadcast command and serves to
        get the serial number of the module.
        
        >>> from basecommands import BaseCommands
        >>> import binascii
        >>> b = BaseCommands()
        >>> p = b.get_negative_acknowledge()
        >>> print binascii.b2a_hex(p)
        fd0800ffffff60
        """
        packet = self.pack(serno=16777215,cmd=0x08)
        return packet
        
    def get_parameter(self,serno,table,param):
        """ COMMAND TO READ A PARAMETER.
        
        Command to read a parameter from one of the different parameter
        tables in the slave module.
        
        >>> from basecommands import BaseCommands
        >>> import binascii
        >>> b = BaseCommands()
        >>> p = b.get_parameter(31002,'SYSTEM_PARAMETER_TABLE','SerialNum')
        >>> print binascii.b2a_hex(p)
        fd0a031a7900290100c4
        >>> p = b.get_parameter(31002,10,'SerialNum')
        >>> print binascii.b2a_hex(p)
        fd0a031a7900290100c4
        """
        param_tables = self.param_tables
        
        # select the right table by it's name or parameter
        # group get-command-number.
        if type(table) is int:
            table = [t for t in param_tables if t['Table']['Get'] == table]
        elif type(table) is str:
            table = [t for t in param_tables if t['Table']['Name'] == table]
        else:
            table = None
        
        if not table:
            raise BaseCommandsError('Could not find spezified Table!')
        else:
            table = table[0]
        
        cmd = table['Table']['Get']
        no_param = table[param]['No']
        packet = self.pack(serno,cmd,no_param)
        
        return packet
            
    def set_parameter(self,serno,table,param,value):
        """ COMMAND TO SET A PARAMETER.
        
        Command to write a parameter to one of the different parameter
        tables in the slave module. It will checkt if the value has the
        right type and if this parameter is writable, according tho the
        tables.
        
        TODO: Check the value!
        
        >>> from basecommands import BaseCommands
        >>> import binascii
        >>> b = BaseCommands()
        >>> p = b.set_parameter(31002,'PROBE_CONFIGURATION_PARAMETER_TABLE',\
                                'DeviceSerialNum',31003)
        >>> print binascii.b2a_hex(p)
        fd11051a79002c0c00791bab
        >>> p = b.set_parameter(31002,17,'DeviceSerialNum',31003)
        >>> print binascii.b2a_hex(p)
        fd11051a79002c0c00791bab
        """
        param_tables = self.param_tables
        
        # select the right table by its name or parameter
        # group set command number.
        if type(table) is int:
            table = [t for t in param_tables if t['Table']['Set'] == table]
        elif type(table) is str:
            table = [t for t in param_tables if t['Table']['Name'] == table]
        else:
            table = None
        
        if not table:
            raise BaseCommandsError('Could not find spezified Table!')
        else:
            table = table[0]
        
        cmd = table['Table']['Set']
        no_param = table[param]['No']
        status = table[param]['Status']
        length = table[param]['Length'] * 2
        value = '%X' % value
        value.zfill(length)
        
        if not status == 'WR':
            raise BaseCommandsError('Parameter is not writeable!')
        
        if not len(value) <= length:
            raise BaseCommandsError('Parameter has the wrong length!')
            
        packet = self.pack(serno,cmd,no_param,value)
        return packet

    def do_tdr_scan(self,serno,start,end,span,count):
        """ DO TDR SCAN
        
        Before using this command, the event TDRScan must be entered
        through writing the parameter Event in Action Parameter to
        1.Then read the parameter again to see if the event has been
        successfully entered. If 0x81(129) is returned, it is successful.
        This command may be carried out now. If 0x01(1) is returned, this
        means that the event has not been entered. This should be checked
        until 0x81 is gotten.
        
        >>> from basecommands import BaseCommands
        >>> import binascii
        >>> b = BaseCommands()
        >>> p = b.do_tdr_scan(30001,1,126,2,64)
        >>> print binascii.b2a_hex(p)
        fd1e00317500da
        """
        start = "%02X" % start
        end = "%02X" % end
        span = "%02X" % span
        count = "%04X" % count
        param = start + end + span + count
        packet = self.pack(serno,0x1e,no_param=None,ad_param=None,param=param)
        return packet
        
    def get_epr_image(self,serno,pagenr):
        """ VERY SPECIAL COMMAND.
        
        pagenr shold be a string hex value!
        
        >>> from basecommands import BaseCommands
        >>> import binascii
        >>> b = BaseCommands()
        >>> p = b.get_epr_image(30001,7)
        >>> print binascii.b2a_hex(p)
        fd3c00317500a1
        """
        pagenr = '%02X' % pagenr
        param = 'FF' + pagenr
        packet = self.pack(serno,0x3c,no_param=None,ad_param=None,param=param)
        return packet
        
    def set_epr_image(self,serno,pagenr,page):
        """ VERY SPECIAL COMMAND.
        
        pagenr shold be a string hex value!
        
        >>> from basecommands import BaseCommands
        >>> import binascii
        >>> b = BaseCommands()
        >>> p = b.set_epr_image(30001,7,'FFFFFFFFFE000000')
        >>> print binascii.b2a_hex(p)
        fd3d003175006c
        """
        pagenr = '%02X' % pagenr
        param = 'FF' + pagenr + page
        packet = self.pack(serno,0x3d,no_param=None,ad_param=None,param=param)
        return packet

if __name__ == "__main__":
    import doctest
    doctest.testmod()
