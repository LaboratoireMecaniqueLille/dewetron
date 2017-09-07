#coding: utf-8
from __future__ import print_function

import serial

#from DAQP_STG import Dewe_DAQP_STG

class DefinitionError(Exception):
  def __init__(self,msg=""):
    self.msg = msg
  def __str__(self):
    return "[Definition error:]"+str(self.msg)

class Dewe_module(type):
  """
  This metaclass defines the type for the modules in a Dewetron rack,
  it keeps track of all the supported classes
  """
  modules={}
  needed_methods = ["set_address","check_address","get_config"]

  #def __new__(metacls,name,bases,dict):
  #  return type.__new__(metacls,name,bases,dict)

  def __init__(cls,name,bases,dict):
    type.__init__(cls,name,bases,dict)
    if name in Dewe_module.modules:
      raise DefinitionError("Dewe_module: Cannot redefine "+name+" module")
    Dewe_module.modules[name] = cls

    missing_methods = []
    for m in Dewe_module.needed_methods:
      if not m in dict:
        missing_methods.append(m)
    if missing_methods:
      raise DefinitionError("Class "+name+" is missing methods: "+str(
                            missing_methods))
    del missing_methods


class Dewetron(object):
  """This class represents a Dewetron signal conditionning rack, 
  it can hold multiple modules"""
  def __init__(self,port,channels,baud=9600,reset_addresses=False):
    self.port = port
    self.baud = baud
    self.ser = serial.Serial(port,baudrate=baud,timeout=.5)
    self.mod = []
    a = 0
    for s in channels:
      self.mod.append(Dewe_module.modules["Dewe_"+s.replace('-','_')](a))
      a+=1

    if reset_addresses or not self.check_addresses():
      print("Starting address configurator...")
      self.set_addresses(reset=reset_addresses)
      while not self.check_addresses():
        print("Error! Were you pressing the corresponding button each time?")
        if raw_input("Retry ?([y]/n)> ").lower() in ["","y","o"]:
          self.set_addresses()
        else:
          break


  def check_addresses(self):
    for m in self.mod:
      if not m.check_address(self.ser):
        print("Module",m.mod_address,"has an incorrect address!")
        return False
    print("Addresses are correct! This does not necessarily mean their address corresponds to the number on the rack !! (Use reset_addresses=True to be sure of that!)")
    return True

  def set_addresses(self,reset=False):
    """This method is used to set the addresses of each module.
    if reset=True, all of the addresses will be reassigned, even if they seem correct.
    Else, They will only be reassigned if the module type is different (default)
    Be sure to use reset=True when the modules have been replaced/moved.
    """
    a = 0
    print("Setting addresses!")
    print("The button on the corresponding module must be pressed when setting the address")
    print("It only needs to be done once after the modules have been changed")
    for m in self.mod:
      m.set_address(self.ser,a,reset=reset)
      a+=1
    raw_input("Done, press enter to continue")

  def get_config(self,mod_address):
    return self.mod[mod_address].get_config(self.ser)

