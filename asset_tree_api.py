import uuid

from tellus_core.db_utils import MongoClient


class NotFoundException(Exception):
    pass


class AssetTree(object):
    def __init__(self):
        self.mongo_client = MongoClient('AssetTree')
        self._tree_data = self.get_tree()

    def get_tree(self):
        data = self.mongo_client.find_one() or {}
        return data.get('data', {})

    def update_tree(self, data=None):
        if data is None:
            data = self._tree_data
        else:
            self._tree_data = data
        return self.mongo_client.update_one({}, {'$set': {'data': data}}, upsert=True)

    def find(self, uid, tree=None, pop_dict=False):
        if tree is None:
            tree = self._tree_data
        for _id, data in tree.items():
            if _id == uid:
                if pop_dict:
                    tree.pop(_id)
                return data
            else:
                return self.find(uid, data['children'], pop_dict)

    def create(self, name, parent_id=None):
        create_data = {str(uuid.uuid4()): {'name': name, 'children': {}}}
        if not parent_id:
            self._tree_data.update(create_data)
        else:
            data = self.find(parent_id)
            print(parent_id)
            if data:
                data['children'].update(create_data)
            else:
                raise NotFoundException('parent_id not found')

        self.update_tree()
        return create_data

    def rename(self, name, _id):
        data = self.find(_id)
        if data:
            data['name'] = name
            return self.update_tree()
        raise NotFoundException('id not found')

    def delete(self, _id):
        data = self.find(_id, pop_dict=True)
        if data:
            return self.update_tree()
        raise NotFoundException('id not found')

    def _find_and_create(self, name, parent_id, tree_data=None):
        if tree_data is None:
            tree_data = self._tree_data
        for _id, data in tree_data.items():
            if data['name'] == name:
                return _id, data['children']

        data = self.create(name, parent_id)
        _id = list(data.keys())[0]
        return _id, data[_id]['children']

    def batch_create(self, tree_path, parent_id=None):
        tree_names = tree_path.replace('\\', '/').split('/')
        if not parent_id:
            data = None
        else:
            data = self.find(parent_id)
            if not data:
                raise NotFoundException('id not found')
            data = data['children']

        for name in tree_names:
            print(self._tree_data)
            parent_id, data = self._find_and_create(name, parent_id, data)

        #fixme 还有bug


if __name__ == '__main__':
    at = AssetTree()
    print(at.get_tree())
    # at.delete('c88d26df-1431-424c-9add-1dbf25d5b813')
    at.batch_create('6/66/666', 'a909d523-eefa-4076-b46a-d03678f68bb3')
    print(at.get_tree())
