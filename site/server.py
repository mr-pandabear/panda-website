import os

from flask import Flask, send_from_directory
from flask import render_template
import json

app = Flask(__name__)

def get_hosts():
    return ['1','2','3','4']

@app.route('/static/<path:path>')
def raw_file():
    return send_from_directory('static', path)

@app.route('/hosts')
def hosts():
    return json.dumps(get_hosts())

@app.route('/')
def index():
    info = {}
    info['num_coins'] = "{:,}".format(200000)
    info['num_wallets'] = "{:,}".format(200000)
    info['source_url']= "{:,}".format(200000)
    info['num_nodes']= "{:,}".format(200000)
    info['pending_transactions']= "{:,}".format(200000)
    info['transactions_per_second']= "{:,}".format(200000)
    info['transaction_volume']= "{:,}".format(200000)
    info['avg_transaction_size']= "{:,}".format(200000)
    info['avg_transaction_fee']= "{:,}".format(200000)
    info['difficulty']= "{:,}".format(200000)
    info['current_block']= "{:,}".format(200000)
    info['last_block_time']= "{:,}".format(200000)
    info['transactions'] = ['c','d','e']
    info['source_url'] = 'http://ec2-35-86-117-146.us-west-2.compute.amazonaws.com:3000'
    info['hosts'] = get_hosts()
    return render_template('index.html', info=info, hosts=info['hosts'], transactions=info['transactions'])

app.run(host='0.0.0.0', port=80)

