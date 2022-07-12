from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from redistimeseries.client import Client as RedisTimeseries
from redisbloom.client import Client as RedisBloom


# From our local file
from load_data import load_data

from os import environ

import redis

import json
import re
import string
import time

app = Flask(__name__,
            static_url_path='/docs', 
            static_folder='docs',
)

bootstrap = Bootstrap()

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

rts = RedisTimeseries(
    host=redis_server,
    port=redis_port,
    password=redis_password
    )

rb = RedisBloom(
    host=redis_server,
    port=redis_port,
    password=redis_password
    )


nav = Nav()
topbar = Navbar('',
    View('Home', 'index'),
    View('Graphs', 'graphs'),
    View('ReloadDB', 'reloaddb'),
    View('Presentation', 'preso'),
)
nav.register_element('top', topbar)

@app.route('/')
def index():
   if rdb.exists("CONFIG") < 1:
       load_data()
   return render_template('index.html')


@app.route('/firemessage', methods = ['POST'])
def firemessage():
   f = request.form.to_dict()
   f['range'] = str(int(int(f['messages']) * int(f['range'])/100))
   rdb.xadd('fill', f)
   return redirect("/graphs", code=302)

@app.route('/graphs')
def graphs():
   ts = rts.mrange(0, int(time.time())*1000, bucket_size_msec=10000, filters=['Type=Final'])
   labels = []
   filtered = []
   unfiltered = []
   last_tick = 0
   # be sure to get all of the unfiltered first otherwise the series gets truncated
   for x in ts[1]['unfiltered'][-1]:
      labels.append(time.strftime('%H:%M:%S', time.localtime(x[0])))
      unfiltered.append(x[1])
   for x in ts[0]['filtered'][-1]:
      filtered.append(x[1])
      last_tick = x[1]
   # we need to backfill the filtered timeseries to match the length of the unfiltered
   for x in range(len(filtered), len(unfiltered)):
      filtered.append(last_tick)
   return render_template('stats.html', filtered=filtered, unfiltered=unfiltered,labels=labels)



@app.route('/reloaddb')
def reloaddb():
   return render_template('flush.html')

@app.route('/flushdb', methods = ['POST'])
def flushdb():
   rdb.flushdb()
   load_data()
   return redirect("/", code=302)


@app.route('/preso')
def preso():
   return redirect("/docs/index.html", code=302)



if __name__ == '__main__':
   bootstrap.init_app(app)
   nav.init_app(app)
   app.debug = True
   app.run(port=5000, host="0.0.0.0")
