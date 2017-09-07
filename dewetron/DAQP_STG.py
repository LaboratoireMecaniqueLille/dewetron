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

class Dewe_DAQP_STG(object):
  __metaclass__ = Dewe_module

  def __init__(self,address):
    self.name = "DAQP-STG"
    self.type_id = "35"
    self.mod_address = address
    self.mod_address_str = "%02i"%self.mod_address

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
    return r
