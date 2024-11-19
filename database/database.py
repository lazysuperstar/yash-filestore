import motor.motor_asyncio
from config import DB_URI, DB_NAME

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user
            
    # async def present_user(user_id : int):
    #     found = user_data.find_one({'_id': user_id})
    #     return bool(found)

    # async def add_user(user_id: int):
    #     user_data.insert_one({'_id': user_id})
    #     return
    
    def new_user(self, id):
        return dict(
            _id=int(id),                                   
            file_id=None,
            caption=None
        )

    async def add_user(self, user_id: int):
        self.col.insert_one({'_id': user_id})
        return
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)
    
    async def present_user(self, user_id : int):
        found = self.col.find_one({'_id': user_id})
        return bool(found)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users
    
    async def full_userbase(self):
        user_docs = self.col.find({})
        user_ids = []
        for doc in user_docs:
            user_ids.append(doc['_id'])
            
        return user_ids

    async def del_user(self, user_id: int):
        self.col.delete_one({'_id': user_id})
        return
    
    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption', None)

    # async def full_userbase():
    #     user_docs = user_data.find()
    #     user_ids = []
    #     for doc in user_docs:
    #         user_ids.append(doc['_id'])
            
    # return user_ids

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})
    
    # def addthumb(chat_id, file_id):
    #     user_data.update_one({"_id": chat_id}, {"$set": {"file_id": file_id}})


    # def set_thumbnail(id, file_id):
    #     user_data.update_one({'id': int(id)}, {'$set': {'file_id': file_id}})


    # async def get_thumbnail(id):
    #     try:
    #         thumbnail = user_data.find_one({'id': int(id)})
    #         if thumbnail:
    #             return thumbnail.get('file_id')
    #         else:
    #             return None
    #     except Exception as e:
    #         print(e)
    # # Born to make history @LazyDeveloper ! => Remember this name forever <=

    # async def set_caption(id, caption):
    #     user_data.update_one({'id': int(id)}, {'$set': {'caption': caption}})

    # async def get_caption(id):
    #     user = user_data.find_one({'id': int(id)})
    #     return user.get('caption', None)

    # async def get_lazy_thumbnail(id):
    #     user = user_data.find_one({'id': int(id)})
    #     return user.get('thumbnail', None)

    # async def get_lazy_caption(id):
    #     user = user_data.find_one({'id': int(id)})
    #     return user.get('lazy_caption', None)

    # async def set_lazy_thumbnail(id, thumbnail):
    #     user_data.update_one({'id': id}, {'$set': {'thumbnail': thumbnail}})

    # Born to make history @LazyDeveloper ! => Remember this name forever <=
db = Database(DB_URI, DB_NAME)
