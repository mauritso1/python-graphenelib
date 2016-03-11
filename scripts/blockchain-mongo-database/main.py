from grapheneapi.grapheneclient import GrapheneClient
from grapheneapi.graphenewsprotocol import GrapheneWebsocketProtocol
from pymongo import MongoClient
import datetime
import time
from pprint import pprint
import json

client = MongoClient()
db = client['bitshares']


class Config(GrapheneWebsocketProtocol):
    wallet_host           = "localhost"
    wallet_port           = 8092
    wallet_user           = ""
    wallet_password       = ""

#    witness_url           = "ws://localhost:8090/"
    witness_url           = "ws://10.0.0.16:8090/"
    witness_user          = ""
    witness_password      = ""


def process_transactions(txs, block):
    for i, tx in enumerate(txs):
        storeOperations(tx["operations"], block, i)


def storeOperations(ops, block, txIndex):
    txid = block["transaction_ids"][txIndex]
    for i, op in enumerate(ops):
        data = op[1]
        data["opType"] = op[0]
        data["timestamp"] = datetime.datetime.strptime(block["timestamp"], "%Y-%m-%dT%H:%M:%S")
        print(" - Transaction: %s / opType: %d" % (txid, op[0]))
        db.operations.update({"_id" : "%s-%d" % (txid, i)}, op[1], True)


def loadConfig() :
    c = db.config.find_one({"key": "configuration"})
    return c


def setConfig(key, value) :
    result = db.config.update_one(
        {"key": "configuration"},
        {"$set": {key : value},
         "$currentDate": {"lastModified": True},
         }, True)
    return result.matched_count


if __name__ == '__main__':
    graphene = GrapheneClient(Config)

    info = graphene.rpc.info()
    head_block_num = info["head_block_num"]

    conf = loadConfig()
    if conf and "last_block" in conf:
        start_block_num = conf["last_block"]
    else:
        start_block_num = 1

    for blockid in range(start_block_num, head_block_num):
        block = graphene.rpc.get_block(blockid)
        print("Block #%d" %blockid)
        process_transactions(block["transactions"], block)
        setConfig("last_block", blockid)
