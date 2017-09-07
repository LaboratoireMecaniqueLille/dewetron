#coding: utf-8
from __future__ import print_function

from dewetron import Dewe_module

table_range_gain = { #mV/V
  "01": 1000,
  "02": 500,
  "03": 200,
  "04": 100,
  "05": 50,
  "06": 20,
  "07": 10,
  "08": 5,
  "09": 2,
  "0A": 1,
  "0B": .5,
  "0C": .2,
  "0D": .1,
  "CC": "CUSTOM"}

table_range_V = { #mV
  "00": 10000,
  "01": 5000,
  "02": 2000,
  "03": 1000,
  "04": 500,
  "05": 250,
  "06": 100,
  "07": 50,
  "08": 25,
  "09": 10,
  "0A": 5,
  "0B": 2.5,
  "0C": 1,
  "0D": .5,
  "CC": "CUSTOM"}

table_excitation_v = { #V
    "0":0,
    "1":.25,
    "2":.5,
    "3":1,
    "4":2.5,
    "5":5,
    "6":10,
    "7":12,
    "C":"CUSTOM"
  }

table_excitation_i = { #mA
    "0":.1,
    "1":.2,
    "2":.5,
    "3":1,
    "4":2,
    "5":5,
    "6":10,
    "7":20,
    "C":"CUSTOM"
  }

table_filter = { #Hz
  "00":300000,
  "01":100000,
  "02":30000,
  "03":10000,
  "04":3000,
  "05":1000,
  "06":300,
  "07":100,
  "08":30,
  "09":10}

table_mode = {
  "0":"Full bridge",
  "1":"Half bridge",
  "2":"Quarter bridge, 120 Ohm, 3-wire",
  "3":"Quarter bridge, 350 Ohm, 3-wire",
  "4":"Quarter bridge, 120 Ohm, 4-wire",
  "5":"Quarter bridge, 350 Ohm, 4-wire",
  "6":"Voltage",
  "7":"Resistance",
  "8":"PT100",
  "9":"PT200",
  "A":"PT500",
  "B":"PT1000",
  "C":"PT2000",
  "D":"CUSTOM 1",
  "E":"CUSTOM 2",
  "F":"CUSTOM 3",
  }

table_shunt = {
    "0": "Disabled",
    "1": "Resistor 1 (175 kOhm)",
    "2": "Resistor 2 (59.88 kOhm)",
    "3": "Resistor 3 (custom)",
    }

class Dewe_DAQP_STG(object):
  __metaclass__ = Dewe_module

  def __init__(self,address):
    self.name = "DAQP-STG"
    self.type_id = "35"
    self.mod_address = address
    self.mod_address_str = "%02i"%self.mod_address
    self.pad = lambda i,l: '%0{}x'.format(l)%i if isinstance(i,int) else\
        str(i)[0:l].rjust(l,'0')

  def check_address(self,ser):
    ser.write("??%02i\r"%self.mod_address)
    r = ser.read(20)

    if len(r) == 0:
      print("No module replied with address",self.mod_address)
    #print(r)
    return r[1:3] == "%02i"%self.mod_address and r[3:5] == self.type_id

  def set_address(self,ser,mod_addr,reset=False):
    self.mod_address = mod_addr
    if reset or not self.check_address(ser):
      print("Setting address for module",mod_addr,"module type:",self.name)
      raw_input("Press the corresponding button and press enter when ready")
      ser.write("##%02iSETD\r"%mod_addr)

  def get_config(self,ser):
    ser.write("??%02i\r"%self.mod_address)
    r = ser.read(20)
    print("REPLY:",r)
    assert r[0:5] == "!%02i35"%self.mod_address,"Incorrect reply!"
    self.input_range = r[5:7]
    self.filter = r[7:9]
    d = {'input_range':self.input_range,'filter':self.filter}
    i = 9
    for s in ['excitation',
              'short_circuit',
              'shunt_func',
              'shunt',
              'mode',
              'filter_type',
              'exc_mode',
              'special',
             ]:
      setattr(self,s,r[i])
      d[s] = r[i]
      i+=1
    return d

  def print_config(self,ser):
    conf = self.get_config(ser)
    exc_mode = "Current" if int(conf['exc_mode']) else "Voltage"
    print("== Config for module %d (DAQP-STG) =="%self.mod_address)
    print("  - Mode:",table_mode[conf['mode']])
    print("  - Input range:",table_range_gain[conf['input_range']],"mV/V")
    print("  - Excitation mode:", exc_mode)
    if exc_mode == "Voltage":
      print("  - Excitation:",table_excitation_v[conf['excitation']],'V')
    else:
      print("  - Excitation:",table_excitation_i[conf['excitation']],'mA')
    print("  - Filter:",table_filter[conf['filter']],'Hz')
    print("  - Filter type:","Bessel" if int(conf['filter_type'])\
        else "Butterworth")
    print("  - Shunt:", "Activated" if int(conf['shunt']) else "Deactivated")
    print("  - Shunt function:", table_shunt[conf['shunt_func']])
    print("  - Short circuit:","Activated" if int(conf["short_circuit"])\
        else "Deactivated")


  def set_config(self,ser,**kwargs):
    config = self.get_config(ser)
    for k in kwargs:
      assert k in config,"Invalid parameter:"+str(k)
      config[k] = kwargs[k]
    m = '##%02i'%self.mod_address
    m += self.pad(config['input_range'],2)
    m += self.pad(config['filter'],2)
    for s in ['excitation',
              'short_circuit',
              'shunt_func',
              'shunt',
              'mode',
              'filter_type',
              'exc_mode',
             ]:
      m += self.pad(config[s],1)
    assert len(m) == 15,"Invalid args"
    ser.write(m+'\r')
    r = ''
    while r[-1:] != '\r':
      r += ser.read(1)
    if "NOACK" in r:
      raise IOError("Serial com error!")

