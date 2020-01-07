'''
here we are making a blockchain. in which a block contains index, timestamp, proof, 
previous hash.
'''

'''
here we have various lib imported. json is used to send our data easily over network
so we can easily interact with blockchain. flask is used for making a web application
to work.
'''
import datetime
import hashlib
import json
from flask import Flask, jsonify

'''
first we create a class named Blockchain. we have a constructor of it. functions are
create_a_block, proof_of_work, hash, and so on.
'''
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_a_block(proof = 1, previous_hash = '0')
    
    def create_a_block(self, proof, previous_hash):
        block = {'index' : len(self.chain) + 1,
                 'timestamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash}
        self.chain.append(block)
        return block
    
    def get_last_block(self):
        return self.chain[-1]
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        find_proof = False
        while find_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                find_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def is_valid(self, chain):
        curr_index = 1
        previous_block = chain[0]
        while curr_index < len(chain):
            previous_hash = self.hash(previous_block)
            block = chain[curr_index]
            if block['previous_hash'] != previous_hash:
                return False
            proof = block['proof']
            previous_proof = previous_block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = chain[curr_index]
            curr_index += 1
        return True
    
blockchain = Blockchain()

app = Flask(__name__)

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_last_block()
    previous_hash = blockchain.hash(previous_block)
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    block = blockchain.create_a_block(proof, previous_hash)
    response = {'Block' : block,
                'message' : 'congratulations, you mined a block'}
    
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain' : blockchain.chain,
                'length' : len(blockchain.chain)}
    
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    response = {'status' : blockchain.is_valid(blockchain.chain)}
    
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)
