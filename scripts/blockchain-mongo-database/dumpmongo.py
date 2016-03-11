from graphenebase.transactions import getOperationNameForId
import json
from pymongo import MongoClient
import time
import datetime

client = MongoClient()
db = client['bitshares']


def dropDatabase():
    db.operations.drop()


def dumpDatabase():
    data = db.operations.find()
    for d in data :
        print(json.dumps(d, indent=4))


def getOpHistogram():
    data = db.operations.aggregate(
        [{"$group" : {
            "_id" : "$opType",
            "num" : {"$sum" : 1}
            }}]
        )
    for d in data :
        d["_id"] = getOperationNameForId(d["_id"])
        print(json.dumps(d, indent=4))


def getMonthlyHistogram():
    data = db.operations.aggregate(
        [{"$group" : {
            "_id" : {
                "optype"  : "$opType",
                "date" : {"month" : {"$month": "$timestamp"},
                          "year" : {"$year": "$timestamp"},
                          "day" : {"$dayOfMonth": "$timestamp"}
                          },
               },
               "num" : {"$sum" : "$opType"},
        }}])
    for d in data :
        #d["_id"] = getOperationNameForId(d["_id"])
        print(json.dumps(d, indent=4))

if __name__ == '__main__':
    # dumpDatabase()
#    getOpHistogram()
    # dropDatabase()
    getMonthlyHistogram()

# >>> d = datetime.datetime(2009, 11, 12, 12)
# >>> for post in posts.find({"date": {"$lt": d}}).sort("author"):
# ...   print post
# http://api.mongodb.org/python/current/tutorial.html
# https://docs.mongodb.org/manual/reference/sql-aggregation-comparison/
