#!/usr/bin/env python3 

from redisbloom.client import Client as RedisBloom
from redistimeseries.client import Client as RedisTimeseries

import csv
import redis
import fileinput

from os import environ

def load_data():

  if environ.get('REDIS_SERVER') is not None:
     redis_server = environ.get('REDIS_SERVER')
  else:
     redis_server = 'localhost'
  
  if environ.get('REDIS_PORT') is not None:
     redis_port = int(environ.get('REDIS_PORT'))
  else:
     redis_port = 6379
  
  if environ.get('REDIS_PASSWORD') is not None:
     redis_password = environ.get('REDIS_PASSWORD')
  else:
     redis_password = ''
  
  
  rdb = redis.Redis(
      host=redis_server,
      port=redis_port,
      password=redis_password
      )
  rb = RedisBloom(
      host=redis_server,
      port=redis_port,
      password=redis_password
      )
  rts = RedisTimeseries( 
      host=redis_server,
      port=redis_port,
      password=redis_password
      )
  
  rdb.set("CONFIG", "YES")

  rts.create('s-unfiltered', retention_ms=60000)
  rts.create('s-filtered', retention_ms=60000)
  rts.create('unfiltered', labels={'Type':'Final'}, retention_ms=86400000)
  rts.create('filtered', labels={'Type':'Final'}, retention_ms=86400000)
  rts.createrule('s-unfiltered', 'unfiltered', 'last', 1000)
  rts.createrule('s-filtered', 'filtered', 'last', 1000)
  
  
  for gear in ['./dedup.py']:
      file = open(gear,mode='r')
      g = file.read()
      rdb.execute_command('RG.PYEXECUTE', g)
      file.close()

  if environ.get('REDIS_SCRABBLE') is not None:
    for line in fileinput.input("2019_Collins_Scrabble_Words.txt"):
      rb.bfAdd("Scrabble-Bloom", line.rstrip())

if __name__ == "__main__":
    load_data()
