import logging
import time
import pymongo


class CacheManager:
    def __init__(self, ttl):
        self.cache = {}
        self.ttl = ttl
        self.cache_timestamps = {}

    def get_cached_data(self, key):
        current_time = time.time()
        if key in self.cache and (current_time - self.cache_timestamps[key]) < self.ttl:
            return self.cache[key]
        return None

    def set_cache_data(self, key, data):
        current_time = time.time()
        self.cache[key] = data
        self.cache_timestamps[key] = current_time
        logging.info("Cache updated for key: %s", key)

    def clear_expired_cache(self):
        current_time = time.time()
        expired_keys = [key for key, timestamp in self.cache_timestamps.items() if
                        (current_time - timestamp) >= self.ttl]
        for key in expired_keys:
            del self.cache[key]
            del self.cache_timestamps[key]
            logging.info("Expired cache cleared for key: %s", key)

    async def refresh_cache(self, db, collections):
        logging.info("Starting cache refresh...")
        for collection_name in collections:
            sort_field = 'date' if collection_name == "posts" else 'dateStart'
            sort_order = pymongo.DESCENDING if collection_name == "posts" else pymongo.ASCENDING

            documents = []
            async for doc in db[collection_name].find().sort(sort_field, sort_order):
                doc['_id'] = str(doc['_id'])
                documents.append(doc)

            cache_key = f"{collection_name}_cache"
            self.set_cache_data(cache_key, documents)

        # Optionally clear expired cache
        self.clear_expired_cache()
        logging.info("Cache refresh completed.")
