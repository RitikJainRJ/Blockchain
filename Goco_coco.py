#Here we are making a cryptocurrency based on blockchain named Goco (Go coin).

'''
library info:-
    datetime:- used for the function now to get current time
    hashlib:- used for getting sha256 hash
    json:- used for exchanging information
    Flask:- used to create a web applicatioin for which we can interact with blockchain
    jsonify:- used for returning the block which is dict as a json format.
    request:- it is used to get the data from the front end which in json format
    uuid4:- used to create a random address for node
    urlparse:- used to parse any url and get netloc from it which is useful.
    requests:- used to get the response from a web link.

methods info of Blockchain class:-
    __init__():- used as constructor to initilize the blockchain with an empty list of
                 chain which contain block, create a genesis block.
    create_block():- used to create a block which get added into the blockchain and also
                     return that block so we can display it.
    get_previous_block():- return previous block.
    hash():- used to return the hash of a block.
    proof_of_work():- it is used to find the proof which make our hash valid and return
                      it.
    is_valid():- return whether a chain is valid or not.
    add_transaction():- used to add transaction in the current block and return the 
                        block number.
    add_node():- used to add a single node in the network.
    replace_chain():- used to replace the chain with the longest chain available in
                      network.
    
methods which we call using postman:-
    mine_block():- used to add new block to the blockchain and return the response the
                   added block.
    get_chain():- return the while blockchain in json format.
    is_valid():- return if chain is valid or not.
    connect_nodes():- used to connect various nodes to form a network.
    replace_chain():- used to get consensus and update the chain.
'''

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
from uuid import uuid4
from urllib.parse import urlparse
import requests

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        block = {'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'transactions' : self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def hash(self, block):
        encode_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encode_block).hexdigest()
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def is_valid(self, chain):
        curr_index = 1
        previous_block = chain[0]
        while curr_index < len(chain):
            block = chain[curr_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            proof = block['proof']
            previous_proof = previous_block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = chain[curr_index]
            curr_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender' : sender,
                                 'receiver' : receiver,
                                 'amount' : amount})
        return len(self.chain) + 1
    
    def add_node(self, address):
        address = urlparse(address)
        self.nodes.add(address.netloc)
        
    def replace_chain(self):
        max_length = len(self.chain)
        new_chain = None
        network = self.nodes
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                chain = response.json()['chain']
                length = response.json()['length']
                if length > max_length and self.is_valid(chain):
                    new_chain = chain
                    max_length = length
        if new_chain:
            self.chain = new_chain
            return True
        return False
        
#object of blockchain class
blockchain = Blockchain()

#address of node on port number 5002
node_address = str(uuid4()).replace('-', '')

#web application to interact in postman
app = Flask(__name__)

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_hash = blockchain.hash(previous_block)
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    blockchain.add_transaction(sender = node_address, receiver = 'Coco', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message' : 'congratulations, you just mined a block',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transactions' : block['transactions']}
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response ={'chain' : blockchain.chain,
               'length' : len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    response = {'message' : blockchain.is_valid(blockchain.chain)}
    return jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some keys are missing, Please check', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message' : f'your transaction is added in bock number {index}'}
    return jsonify(response), 201

@app.route('/connect_nodes', methods = ['POST'])
def connect_nodes():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'Please enter some nodes', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message' : 'All nodes are connected',
                'total nodes' : list(blockchain.nodes)}
    
    return jsonify(response), 201
    
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_replace = blockchain.replace_chain()
    if is_replace:
        response = {'chain' : blockchain.chain,
                    'message' : 'This chain is replaced by a bigger chain'}
    else:
        response = {'chain' : blockchain.chain,
                    'message' : 'not replaced because this is the biggest chain'}
    return jsonify(response), 201

#running the app on port 5002
app.run('0.0.0.0', 5002)


'''
here is template of Json file to use in postman

{
	"sender" : "",
	"receiver" : "",
	"amount" : ""
}


{
	"nodes" : ["http://127.0.0.1:5000",
			   "http://127.0.0.1:5001",
			   "http://127.0.0.1:5002"]
}
'''