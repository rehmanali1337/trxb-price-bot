from pymongo import MongoClient

'''
'''


class WhiteListDB:
    def __init__(self):
        admin = 'admin'
        password = 'RvX7djPqmcmzLPfO'
        host = f'mongodb+srv://{admin}:{password}@cluster0.x7kgu.mongodb.net/UsersDB?retryWrites=true&w=majority'
        self._client = MongoClient(host=host)
        self._db = self._client.users
        self._users = self._db["Users"]

    def add_user(self, user_id):
        self._users.insert_one({
            "user_id": user_id,
        })

    def user_exists(self, user_id):
        return self._users.find_one({"user_id": user_id})

    def remove_user(self, user_id):
        self._users.find_one_and_delete({"user_id": user_id})


if __name__ == '__main__':
    db = WhiteListDB()
    # db.add_user(1)
    db.remove_user(1)
    print(db.user_exists(1))
