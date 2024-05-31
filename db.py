from pymongo import MongoClient

uri = "mongodb://mongo:27017"

db = ()

def connect(): 
    client = MongoClient(uri)
    global db
    db = client['starlink']

def write_data(data: dict | list, collection: str):
    check_or_create_collection(str)
    if isinstance(data, list):
        db[collection].insert_many(data)
    else:
        db[collection].insert_one(data)
    pass

def check_or_create_collection(name: str):
    collection_list = db.list_collection_names()
    if name not in collection_list:
        db.create_collection(name, {
            'timeseries':
                {'timeField':"timestamp",
                'metaField':"metadata",
                'bucketMaxSpanSeconds':3600,
                'bucketRoundingSeconds':3600
                }
            })
        print(f"Created collection: {name}")

