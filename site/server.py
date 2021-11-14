import os
import requests
from flask import Flask, send_from_directory
from flask import render_template
from flask import request
import json
from datetime import datetime

app = Flask(__name__)

def get_hosts():
    return ['http://localhost:3000']

@app.route('/static/<path:path>')
def raw_file():
    return send_from_directory('static', path)

@app.route('/hosts')
def hosts():
    return json.dumps(get_hosts())

@app.route('/block')
def block():
    host = request.args.get('host')
    id = request.args.get('id')
    if host == None:
        host = get_hosts()[0]
    print('id', id)
    resp = requests.get(url=host+'/block/'+str(id))
    info = resp.json()
    print(info)
    info['url'] = host
    ts = int(info['timestamp'])
    info['timestamp'] = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    info['num_transactions'] = len(info['transactions'])
    return render_template('block.html', info=info)

@app.route('/')
def index():
    host = request.args.get('host')
    if host == None:
        host = get_hosts()[0]
    resp = requests.get(url=host + '/stats')
    info = resp.json()
    print(info)
    info['curr_host'] = host
    info['hosts'] = []
    info['transactions_per_second'] = '%.2f' % (info['transactions_per_second'])
    allhosts = get_hosts()
    for currhost in allhosts:
        if currhost != host:
            try:
                resp = requests.get(url=currhost + '/stats')
                currdata = resp.json()
                currdata['url'] = currhost
                info['hosts'].append(currdata)
            except:
                continue

    info['num_nodes'] = len(info['hosts'])
    return render_template('index.html', info=info, hosts=info['hosts'], transactions=info['transactions'])

app.run(host='0.0.0.0', port=80)

