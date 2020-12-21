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

app = Flask(__name__)
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
   rdb.xadd('fill', f)
   return redirect("/graphs", code=302)

@app.route('/graphs')
def graphs():
   ts = rts.mrange(0, -1, bucket_size_msec=1000, filters=['Type=Final'])
   labels = []
   filtered = []
   unfiltered = []
   for x in ts[0]['filtered'][-1]:
      labels.append(time.strftime('%H:%M:%S', time.localtime(x[0])))
      filtered.append(x[1])
   for x in ts[1]['unfiltered'][-1]:
      unfiltered.append(x[1])
   return render_template('stats.html', filtered=filtered, unfiltered=unfiltered,labels=labels)





if __name__ == '__main__':
   bootstrap.init_app(app)
   nav.init_app(app)
   app.debug = True
   app.run(port=5000, host="0.0.0.0")
