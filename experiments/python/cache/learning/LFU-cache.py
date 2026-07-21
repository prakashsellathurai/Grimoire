# Lfu cache
# Least Frequently used - evicts the keys accessed few times when capacity is full. tiles broken 
# by recency (LRU withing sam frequency bucket)
# expected O(1) design
# Keymap : key -> {value, freq, ttl_deadline}
# freqmap: freq -> OrderedDict[key -> sentinel]
# minfreq: int # current min frequency
# Key map enables O(1) lookup
# freqmap enables group keys by frequency 
# minfreq jumps to 1 on any new insert
#
# TTL
# Each key carries a expires_at = now() + ttl on get() the cache checks if expired before returning
# expired entries are logically deleted on access (laxy eviction)
# 
# Eviction strategies
#  Lazy -> check on every get/put, stale key stau in memory until tocuhed -> no background proces
#  Active -> scheduler proactively removes expired keys. keep meory tight but adds complexity
# 
# TTL + LFU interaction
# when key expires and is evicted minFreq must be recomputed The standard trick: only ipdate minFreq to 1 on put() of a brand new key
# 
# Write Behind(write-back)
# writes go to the cache immediately and return success. The cache asynchronously flushes direty entries to DB in background queue
# 
# Dirty bit tracking
#   keyMap: key -> value, freq, ttl, dirty:bool, version:int
# 
# 
# hashmap based approach
# Data structure :
#    without cache invalidation key : value:frequency
#   with cach invalidation : current_min_freq 
#             frequency {keys}
#              key : value,frequency
#    maintaing keys in linkedlist to suppport O(1) insert update
# 
#  1. Hashmap key: (frequency,value)
#  2.frequencies: [list of keys] (use set in python language)
#  3.min_frequency 
#  4 .capacity
#  
#  methods 
#    internal insert(key, frequency, value)
#       insert freq,value into key hashmap
#          append key into frequency hahsmap list
# 
#    get key:
#      1 if key not in cache return -1
#      2  get frequency , value from key hahsmap
#      3 get set from frequency hashmap and remove key
#     4 if minf  == frwquency and above is empty 
#            minf ==1
#            delete frequency entry in frequencies
#     5 insert(key, vaue,frequnecy + 1)
#     return value
#   put key value
#       1.if capcity <= 0 exit
#       2 if key exists in cache update frequency value in origincal hashmap 
#           call hashmap
#       3. if cache size matches capacity 
#                     get minf of frequency and remove
#       4 minf += 1
#       insert key 1 ,value
# 
# 
# 
from collections import OrderedDict, defaultdict
class LFUCache:
    def __init__(self, capcity) -> None:
        self.cap = capcity
        self.key2val = {}
        self.key2freq = {}
        self.freq2key = defaultdict(OrderedDict)
        self.minf= 0 

    def get(self, key):
        # check key not exists
        if key not in self.key2val:
            return -1
        # update frequency by 
        oldfreq = self.key2freq[key]
        self.key2freq[key] = oldfreq + 1
        self.freq2key[oldfreq].pop(key)
        # edge case saves space if current frequency is emoty rempove
        if not self.freq2key[oldfreq]:
            del self.freq2key[oldfreq]
        # add it to new frequency
        self.freq2key[oldfreq + 1][key] = 1
        # update minf frequency if it doesn't exits
        if self.minf not in self.freq2key:
            self.minf += 1
        # return value
        return self.key2val[key]

    def put(self, key,value):
        #check boundary cases
        if self.cap <= 0:
            return
        # if key already in cache udpate value and call get to update 
        # frequency
        if key in self.key2val:
            self.get(key)
            self.key2val[key] = value
            return

        # if cap reaches limit pop from freq2 key via minf and delet from all three ds
        if len(self.key2val) == self.cap:
            delkey, _ = self.freq2key[self.minf].popitem(last=False)
            del self.key2val[delkey]
            del self.key2freq[delkey]  
        # add entry if not exists
        self.key2val[key] = value
        self.key2freq[key] = 1
        self.freq2key[1][key] = 1
        self.minf = 1