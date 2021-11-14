import os
import requests
from flask import Flask, send_from_directory
from flask import render_template
from flask import request
import json

app = Flask(__name__)

def get_hosts():
    return ['http://localhost:3000','http://localhost:8080']

@app.route('/static/<path:path>')
def raw_file():
    return send_from_directory('static', path)

@app.route('/hosts')
def hosts():
    return json.dumps(get_hosts())

@app.route('/')
def index():
    host = request.args.get('host')
    if host == None:
        host = get_hosts()[0]
    resp = requests.get(url=host + '/stats')
    info = resp.json()
    info['curr_host'] = host
    info['hosts'] = []
    info['transactions_per_second'] = '%.2f' % (info['transactions_per_second'])
    allhosts = get_hosts()
    for currhost in allhosts:
        if currhost != host:
            resp = requests.get(url=currhost + '/stats')
            currdata = resp.json()
            currdata['url'] = currhost
            info['hosts'].append(currdata)

    info['num_nodes'] = len(info['hosts'])
    return render_template('index.html', info=info, hosts=info['hosts'], transactions=info['transactions'])

app.run(host='0.0.0.0', port=80)

