#coding: utf-8
from __future__ import print_function
from dewetron import Dewetron

if __name__ == "__main__":
  d = Dewetron("/dev/ttyUSB0",channels=['DAQP-STG']*8,reset_addresses=False)
  print(d.get_config(0))
