## basics
DHT performs the functions of hashtable that stores a key and value pair and lookup the value if key is presents values are not necessary persisted on the disk and it's distributed among multiple machines unlike master slave model all nodes can join and leave network freely.

## Design Exploration
### Circular Doubly-linkedlist
Each node in the list is the machine on the  network each node keeps reference to the next and previous nodes in the list. Ordering determins the next node in the list exampled assign unique random id of k bots to each node arrange the nodes in a ring so the IDs are in increasing in clockwise orer. 

> RingDistance
```
# This is a clockwise ring distance function.
# It depends on a globally defined k, the key size.
# The largest possible node id is 2**k.
def distance(a, b):
    if a==b:
        return 0
    elif a<b:
        return b-a;
    else:
        return (2**k)+(b-a);
```
Each Node is a stand. Hash Table retreiev appropriate node from network and do  a normal hash table lookup. Determine the node for the particular key is same as determining of a particular Node ID. key -> hash to k bits (node ID) -> determine node successor by working clockwise until a nodeID is closest but still greater than key

> findNode
```
# From the start node, find the node responsible
# for the target key
def findNode(start, key):
    current=start
    while distance(current.id, key) > \
          distance(current.next.id, key):
        current=current.next
    return current

# Find the responsible node and get the value for
# the key
def lookup(start, key):
    node=findNode(start, key)
    return node.data[key]

# Find the responsible node and store the value
# with the key
def store(start, key, value):
    node=findNode(start, key)
    node.data[key]=value
```
In real world DHT with each nodes join/leave via a protocol i.e chord join protocol to lookup the succesor of the new node's ID using normal lookup protocol.  during insert sone entruies are copied from predecessor to new node to avoid lookupfailure

during leave operation all entries are copied to predecessor. having dynamic members makes pereformance terrivke O(n)

### Chord Design
It adds layer to access O(logn) performance.each nodes shares finger tabke to all other nodes containg addresses of k nodes  
> update
```
def update(node):
    for x in range(k):
        oldEntry=node.finger[x]
        node.finger[x]=findNode(oldEntry,
                          (node.id+(2**x)) % (2**k))
```
> finger-lookup
```
def findFinger(node, key):
    current=node
    for x in range(k):
        if distance(current.id, key) > \
           distance(node.finger[x].id, key):
            current=node.finger[x]
    return current

def lookup(start, key):
    current=findFinger(start, key)
    next=findFinger(current, key)
    while distance(current.id, key) > \
          distance(next.id, key):
        current=next
        next=findFinger(current, key)
    return current
```
