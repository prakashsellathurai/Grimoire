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