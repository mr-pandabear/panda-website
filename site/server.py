import os
import requests
from flask import Flask, send_from_directory
from flask import render_template
from flask import request
import json
from datetime import datetime

app = Flask(__name__)

HOST_LIST = ['http://ec2-34-216-18-6.us-west-2.compute.amazonaws.com:3000']

def get_hosts():
    global HOST_LIST
    return HOST_LIST

@app.route('/hosts')
def hosts():
    return json.dumps(get_hosts())

@app.route('/add_host')
def add_host():
    global HOST_LIST
    host = request.args.get('host')
    HOST_LIST.append(host)

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
                currdata['url'] = 'RUNNING'
                info['hosts'].append(currdata)
            except:
                currdata['url'] = currhost
                currdata['status'] = 'NO RESPONSE'
                continue

    info['num_nodes'] = len(info['hosts'])
    return render_template('index.html', info=info, hosts=info['hosts'], transactions=info['transactions'])


@app.route('/static/<path:path>')
def raw_file():
    return send_from_directory('static', path)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)

