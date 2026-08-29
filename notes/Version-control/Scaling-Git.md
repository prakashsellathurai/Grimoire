# The Seed
Initial commit for git https://github.com/git/git/commit/e83c5163316 decription as
> Initial revision of "git", the information manager from hell
It started with basic functionalities such as init db , read / write -> tree/cache , show diff, commit-tree. It was being used to develop Linux kernel. Now a indutrial standard

# Scaling
If we want to scale git in a distributed manner standard git servers has some caveats like the core ds in git is packfile -> a binary serialization of code and metadata a blob. every git update is transferred as packfile . Packfile are large binary files in  filesystem context in terms if availability and scalability this dioesn't scale well because git's internal ds a DAG but a packfile is randomly is stored as fragments of other objects across the disc along with every git ops requires random walking of data it performs poorly due to constly roundtrips. to keep ops safe git must live on local high speed disk  hence scalability is limited and availibilty is limited

 three possible approaches to accomplish this, in increasing order of complexity: distribute the filesystem, distribute the packfiles, or distribute Git itself.
 
 # Git without packfiles
 store git blobs as distributed KV store but it doesn't work because git is dag most trivial operation requires walk in dag. roundtrips are expensive A bad design
 
# Github and filesystems 

distribute filesystem instead of peddling with gitdata. github later devloped rpc system so that repositories live on dedicated fileservers and provided good horizontal scalability yet availability and performance for the busiest repositories is poor

## Spokes and consistency
Spokes was developed by github in 2013 which is industry standard still now. a application levek replication for git repositories in their architecture. 
 1. it doesn't distribute git itself, works at packfile level.
 2. it stores all data as actual git repos on  disks
 3. it replicates the git data but keep all copies in sync
 
Spoke is a consensus based distributed system it works by storing several copies of a git repos on different servers.when new data is pushed an orchestrator fans out push so every instance of repository receives a copy the fan out is synchronized with a classic consensus algo called 3 PC(phase commit) so push is accepted if a majority of the nodes acknowledge it.

A git push has 2 componenets : a packfile and a reference transaction (commit id and refereneces to parent and child). during precommit phase we can send packfile and do three phase commit with reference transaction. with every replica is fully synchronized and reads can be safely fetched from any replica.

### caveat
it has constrained horizontal scalabilituy of 3PC. whem spokes was released 3 replicas per repo was sweet spot. in 2026 the average repo for an entreprise is now a massive monorepo 3 replicas are not enough to serve the traffic of such repos. The latency of every step is bound by the slowest of all the servers in the clusters. also rough to operate at scale because every repos to machine mapping table must be maintained. checksummed and constantly updated in the table. since repos at disk is the source of truth. so repair jobs must be scheduled very quickly. 


# Continuity 
Continuity is developed by cursor core primitive is a write ahead log which stores in s3 compatible object storage. when repo receives push a wal entry in s3 is pushed which is never acknowledged until it is persisted . each push is stored as seperate object also simultaneously packfileis written in the disk. uploading wal entry doesnot publish it. A push is only visible once it successfully prepares its reference transaction.s3 writes are batched carefully and git is stored as normal git repo on disks.

## consensus, Replication  and compaction
  repos live everwhere like a warm cache on disk source of truth is always wal on s3. stateless if disk becomes un healthy we can materialize for wal in s3.There's no state and no consensus here. Any server can be the primary. All updates to the write-ahead log are synchronized with an atomic compare-and-swap (CAS) operation on S3. It can have any nuber of replicas it can perform optimistic replication by sending gossip udp packerts aroun dthe clusrer even if packet lossses all read replicas are fully consistent.wal requires periodic compaction primary repos does compaction and result updates in wal since replicas follows wal replicas don;t repack they simply download already compacted packs from s3
  