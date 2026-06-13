#  Lru cache
# if capcity exceeds then least recently used item is evicted
#  Time Bounded LRU 
#
# Structure 
#  cache = ordereddictionary of key: (timestamp, value)
#     maxage and maxsize
# 
# get
#    if key present
#       now - timestamp <= maxage 
#           return value
#       del key
#    return -1
#    
# put 
#   if key present
#       if size +1 > maxsize:
#          popfront
#   set key = (now, value)

from collections import OrderedDict
from time import monotonic, sleep

class TimeBoundedLruCache:
    "LRU Cache that invalidates and refreshes old entries."
    def __init__(self, capacity, ttl) -> None:
        self.cache = OrderedDict()
        self.capacity = capacity
        self.ttl = ttl

    def get(self, key):

        if key not in self.cache:
            return -1
            # Expired
        expiry, value = self.cache[key]
        if monotonic() - expiry > self.ttl:
            del self.cache[key]
            return -1
        # Mark as recently used
        self.cache.move_to_end(key)
        return value   

    def put(self, key, value): 
        # Update existing key
        if key in self.cache:
            del self.cache[key]

        # Insert as most recently used
        self.cache[key] = (monotonic(), value)
        # Evict LRU if over capacity
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

class MultiHitLRUCache:
    """ LRU cache that defers caching a result until
        it has been requested multiple times.

        To avoid flushing the LRU cache with one-time requests,
        we don't cache until a request has been made more than once.

    """
    def __init__(self, capacity,  maxrequests=4096, cache_after=1) -> None:

        self.capacity = capacity
        self.maxrequests = maxrequests
        self.cache_after = cache_after

        self.requests = OrderedDict()
        self.cache = OrderedDict()

    def get(self, key):
        # Already cached
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]

        # Track uncached requests
        self.requests[key] = self.requests.get(key, 0) + 1
        self.requests.move_to_end(key)

        if len(self.requests) > self.maxrequests:
            self.requests.popitem(last=False)

        return -1
            
    def put(self, key, value):
        # Update existing cached value
        if key in self.cache:
            self.cache[key] = value
            self.cache.move_to_end(key)
            return

        # Promote only after enough hits
        count = self.requests.get(key, 0)

        if count > self.cache_after:
            self.requests.pop(key, None)

            self.cache[key] = value
            self.cache.move_to_end(key)

            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
        
        
    
    
    
if __name__ == "__main__":
    cache = TimeBoundedLruCache(capacity=2, ttl=3)
    cache.put(1, "A")
    cache.put(2, "B")
    
    print(cache.get(1))  # A
    cache.put(3, "C")    # Evicts key 2
    
    print(cache.get(2))  # -1
    print(cache.get(3))  # C

    sleep(3)
    print(cache.get(1))  # -1
    print(cache.get(3))  # -1


    cache = MultiHitLRUCache(capacity=2, cache_after=1)
    
    print(cache.get(1))   # -1, request count = 1
    
    cache.put(1, 100)     # not cached yet
    
    print(cache.get(1))   # -1, request count = 2
    
    cache.put(1, 100)     # promoted to cache
    
    print(cache.get(1))   # 100
    


