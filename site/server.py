import os
import requests
from flask import Flask, send_from_directory
from flask import render_template
from flask import request
import json
from datetime import datetime
import random

app = Flask(__name__)

HOST_LIST = [
    'http://35.84.249.159:3000',
    'http://44.227.179.62:3000',
    'http://54.189.82.240:3000'
]

BMB_SCALE_FACTOR = 10000.0

def get_hosts():
    global HOST_LIST
    allPeers = set()
    for host in HOST_LIST:
        try:
            d = requests.get(url=host + '/peers', timeout=2).text
            resp = json.loads(d)
            print("GOT", resp, "FROM", host)
            for peer in resp:
                allPeers.add(peer)
        except:
            continue
    return list(allPeers)

@app.route('/hosts')
def hosts():
    curr = get_hosts()
    random.shuffle(curr)
    return json.dumps(curr)

@app.route('/block')
def block():
    host = request.args.get('host')
    id = request.args.get('id')
    if host == None:
        host = get_hosts()[0]
    resp = requests.get(url=host+'/block/'+str(id))
    info = resp.json()
    info['url'] = host
    ts = int(info['timestamp'])
    for i, t in enumerate(info['transactions']):
        info['transactions'][i]['amount'] /= BMB_SCALE_FACTOR
        info['transactions'][i]['fee'] /= BMB_SCALE_FACTOR
    info['timestamp'] = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    info['num_transactions'] = len(info['transactions'])
    return render_template('block.html', info=info)

@app.route('/wallet')
def wallet():
    host = request.args.get('host')
    id = request.args.get('id')
    if host == None:
        host = get_hosts()[0]
    resp = requests.get(url=host+'/ledger/'+str(id))
    info = resp.json()
    if 'error' in info:
        info['url'] = host
        info['id'] = 0
        info['balance'] = 0
    else:
        info['url'] = host
        info['id'] = id
        info['balance']/=BMB_SCALE_FACTOR
        info['balance'] = '{:,}'.format(info['balance'])
    return render_template('wallet.html', info=info)


@app.route('/')
def index():
    host = request.args.get('host')
    allhosts = get_hosts()
    info = { 'hosts': []}
    found_valid = False
    if host:
        info['curr_host'] = host
    else:
        host = 'http://54.189.82.240:3000'
        info['curr_host'] = host

    for currhost in allhosts:
        try:
            resp = requests.get(url=currhost + '/stats', timeout=2)
            curr = resp.json()
            if("error" in curr):
                info['hosts'].append({'url':currhost, 'status':'ERROR'})
                continue
            if host == currhost or host==None:
                host = currhost
                info = {**curr, **info}
                if not 'node_version' in info:
                    info['node_version'] = 'unknown'
                info['curr_host'] = host
                info['num_coins'] = '{:,}'.format(info['num_coins']+ 7775*50 + 6259000)
                info['transactions_per_second'] = '%.2f' % (info['transactions_per_second'])
                info['transaction_volume'] /= BMB_SCALE_FACTOR
                info['avg_transaction_size'] /= BMB_SCALE_FACTOR
                info['hosts'].append({
                    'url':currhost, 
                    'status':'RUNNING', 
                    'current_block':info['current_block'], 
                    'pending_transactions': info['pending_transactions'],
                    'node_version': info['node_version']
                })
                found_valid = True
            else:
                currdata = {}
                currdata['url'] = currhost
                currdata['status'] = 'RUNNING'
                currdata['current_block'] = curr['current_block']
                currdata['pending_transactions'] = curr['pending_transactions']
                if 'node_version' in curr:
                    currdata['node_version'] = curr['node_version']
                else:
                    currdata['node_version'] = 'unknown'
                info['hosts'].append(currdata)
        except:
            currdata = {}
            currdata['url'] = currhost
            currdata['status'] = 'NO RESPONSE'
            info['hosts'].append(currdata)
            continue

    info['num_nodes'] = len(info['hosts'])
    if (not found_valid):
        info['transactions'] = []
    for i, t in enumerate(info['transactions']):
        info['transactions'][i]['amount'] /= BMB_SCALE_FACTOR
        info['transactions'][i]['fee'] /= BMB_SCALE_FACTOR
    info['transaction_count'] = len(info['transactions'])
    return render_template('index.html', info=info, found_valid=found_valid, hosts=info['hosts'], transactions=info['transactions'])


@app.route('/static/<path:path>')
def raw_file():
    return send_from_directory('static', path)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)

