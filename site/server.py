import os
import requests
from flask import Flask, send_from_directory
from flask import render_template
from flask import request
import json
from datetime import datetime

app = Flask(__name__)

HOST_LIST = [
    'http://ec2-35-86-174-245.us-west-2.compute.amazonaws.com:3000',
    'http://ec2-54-191-163-102.us-west-2.compute.amazonaws.com:3000',
    'http://ec2-34-221-173-233.us-west-2.compute.amazonaws.com:3000',
    'http://ec2-52-12-79-244.us-west-2.compute.amazonaws.com:3000'
]

def get_hosts():
    global HOST_LIST
    return HOST_LIST

@app.route('/hosts')
def hosts():
    return json.dumps(get_hosts())

@app.route('/clear_hosts')
def clear_hosts():
    global HOST_LIST
    HOST_LIST = []
    return json.dumps(get_hosts())

@app.route('/add_host')
def add_host():
    global HOST_LIST
    host = request.args.get('host')
    HOST_LIST.append(host)
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
    allhosts = get_hosts()
    info = { 'hosts': []}
    found_valid = False
    if host:
        info['curr_host'] = host
    for currhost in allhosts:
        try:
            resp = requests.get(url=currhost + '/stats')
            curr = resp.json()
            if("error" in curr):
                info['hosts'].append({'url':currhost, 'status':'ERROR'})
                continue
            if host == currhost or host==None:
                host = currhost
                info = {**curr, **info}
                info['curr_host'] = host
                info['transactions_per_second'] = '%.2f' % (info['transactions_per_second'])
                info['transaction_volume'] /= 10000
                info['avg_transaction_size'] /= 10000
                info['hosts'].append({
                    'url':currhost, 
                    'status':'RUNNING', 
                    'current_block':info['current_block'], 
                    'pending_transactions': info['pending_transactions']
                })
                found_valid = True
            else:
                currdata = {}
                currdata['url'] = currhost
                currdata['status'] = 'RUNNING'
                currdata['current_block'] = curr['current_block']
                currdata['pending_transactions'] = curr['pending_transactions']
                info['hosts'].append(currdata)
        except:
            currdata = {}
            currdata['url'] = currhost
            currdata['status'] = 'NO RESPONSE'
            info['hosts'].append(currdata)
            continue

    info['num_nodes'] = len(info['hosts'])
    print(info)
    if (not found_valid):
        info['transactions'] = []
    return render_template('index.html', info=info, found_valid=found_valid, hosts=info['hosts'], transactions=info['transactions'])


@app.route('/static/<path:path>')
def raw_file():
    return send_from_directory('static', path)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=80)

