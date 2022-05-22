import pymongo
from tellus_core import config


class MongoClient(object):
    def __init__(self, collection):
        self.db_name = config.MONGODB.pop('name')
        self.db_collection = collection

        self._client = pymongo.MongoClient(**config.MONGODB)
        self._database = self._client[self.db_name]
        self._collection = self._database[self.db_collection]

    @property
    def client(self):
        return self._client

    @property
    def database(self):
        return self._database

    @property
    def collection(self):
        return self._collection


    def __getattr__(self, name):
        return getattr(self._collection, name)

    def __repr__(self):
        return 'MongoClient(database=%s, collection=%s)' % (self.db_name, self.db_collection)

    def close(self):
        return self._client.close()


if __name__ == '__main__':
    mc = MongoClient('AssetTree')
    print(mc)
