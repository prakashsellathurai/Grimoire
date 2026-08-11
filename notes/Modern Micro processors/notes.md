> Clock speed and Processors performance are not a same thing 

```
SPECint95	SPECfp95
195 MHz	MIPS R10000	11.0	17.0
400 MHz	Alpha 21164	12.3	17.2
300 MHz	UltraSPARC	12.1	15.5
300 MHz	Pentium II	11.6	8.8
300 MHz	PowerPC G3	14.8	11.4
135 MHz	POWER2	6.2	17.6

```
## Pipelining & Instruction level parallelism 
conventional thinking tells Instructions are excuted one afer another but that's not really what happens in fact post 1980s several instructions are all partially executing at the same time

```
Sequential:
I1: F D E W
I2:         F D E W
I3:                 F D E W

Pipelined:
I1: F D E W
I2:   F D E W
I3:     F D E W
```
with pipelined sequence CPI gets four fold speed withour chnaging clock speed by completing 1 istruction per cycle

At the beginning of each cycle the data and control information are partially processed instruction is held in a pipeline patch

> Today's robots are very primitive, capable of understanding only a
few simple instructions such as 'go left', 'go right' and 'build car'.
> — John Sladek

```
Latch      Latch      Latch      Latch      Latch
  │          │          │          │          │
  █          █          █          █          █
  █  Fetch   █  Decode  █  Execute █ Writeback █
  █──Logic──►█──Logic──►█──Logic──►█──Logic───►█
  █          █          █          █          █
  ▲          ▲          ▲          ▲          ▲
  │          │          │          │          │
Clock────────┴──────────┴──────────┴──────────┘
```

During clock cycle the signals propagatae through combinatrial logic of each stage
since the result from each instruction is available after exeute stage rather than waiting for that value results ar committed to its destination register in writeback stage. To allow this forwarding lines called bypasses are added , going backwards along the pipeline 

```
Fetch -> Latch -> Decode -> Latch -> Execute -> latch -> writeback -> latch

bypass:

writeback -> Decode Latch 
Execute -> Decode Latch
```

The Execute stage made up of several different groups of logic making up functionaly units for eachtype of operations like  int, Float, Branch, MEM

## Deeper Pipelines - Superpipelining
Since the clock speed is limited by the length of the longest slowest stage in the pipeline the logic gates that make up each stage can be subdivided converting the pipeline into super-pipelinewith large number of short stages although the processor takes long time to complete on cycle(latency) there will be more cycles per second processor will be completing 1 instruction per cycle (throughput) so processor will complete more instructions per second(actual performance)

## Multiple Issue - Superscalar
Since EXecute step has bunch of different functional units It can be parrallelised to do this fetch and decode /dispatrch stages need to enhanced so they can decode multiple instructions in parallel

which will significantly increase clock per cycle or Instructions per cycle
The IBM POWER1 processor, the predecessor of PowerPC, was the first mainstream superscalar processor. 
Intel even managed to build a superscalar x86 – the original Pentium – however the complex x86 instruction set was a real problem for them

Today, virtually every processor is a superpipelined-superscalar, so they're just called superscalar for short. Strictly speaking, superpipelining is just pipelining with a deeper pipe anyway.

## Explicit parallelism - VLIW
Instructions sets can be designed to be explicit groups to be executed in parallel. it eliminates the need for complex dependency checking logic in dispach stage which makes processor easier to scale and design

In this  instructions are really the group of sub instructions and thus instructions themselves are very long often 128 bits more hence the name Very long instruction word each instruction contain information for multiple parallel operations

in VLIW processor every other process is same except decode/dispatch is much simpler.VLIW is not interlocked they donpt check fpr dependencies between instructions.As a result the compiler need to insert the appropriate number of cycles between dependent instructions called NO-ops(No operations).The programmable shaders in graphics processors (GPUs) are sometimes VLIW designs, as are many digital signal processors (DSPs)

## Instrcution Dependencies & Latencies
We cannot just stack the till n-stage pipeline and issue n scale superpipeline because instructions that depend on other cannot be executed in parallel. The number of cycle between when an instruction reaches the execute stag and when its result is available for use by another instructions is called instruction's latency. The deeper the pipeline the more stages and longer the latency.

## Branches & Branch prediction
```c
if (a > 7) {
    b = c;
} else {
    b = d;
}
```
creates
```assembly
cmp a, 7    ; a > 7 ?
ble L1
mov c, b    ; b = c
br L2
L1: mov d, b    ; b = d
L2: ...
```

If a pipelined processor executes the above instructions by the time conditional branch at line 2 reaches the execute stage the processor must have already fetched and decoded the next couple of instructions. It won't know until coditional branch gets to execute stage. TO avoid that processor takes a guess and speculativelevly excutes the instruction sbut they don't writeback the instructions and will be cancelled which is a waster of compute.

two ways to over come, static branch prediction -> compiler marks the branch to tell the processor which way to go. which need the processor to be smart to make right guess which is not easy for other branches than For loops

other alternative guess at runtime i.e dynamic branch prediction . it uses on -chip branch prediction tables containing the addresses of recent nranches and a bit indication whether a branch was taken or not last time. In reality two bits (for loop  back edges).
even with best branch prediction techniques are sometimes wrong which results instrcutions being cancelled called as mispredict penality. pentium with 12 stage pipeline with mispredict penality of 10 - 15 cycles. very deep pipelines naturally suffer from diminishing returns, because the deeper the pipeline, the further into the future you must try to predict, the more likely you'll be wrong, and the greater the mispredict penalty when you are.

## Eliminating Branches with Predication
A new instruction calle cmovle  for "conditional move if less than or equal".This instruction works by executing as normal, but only commits itself if its condition is true (in the condition flags set by the most recent compare instruction). This is called a predicated instruction, because its execution is controlled by a predicate (a true/false test).


## Instruction Scheduling, Register Renaming & OOO
Now Branches and long latency instructions are causing bubbles in the pipeline then empty cycles can be used to do other work. To Achieve this instructions in the program must be reordered so that while one instruction us waiting other instructios can execute

- approach 1 - reordering in hardware at runtime Doing Dynamic instruction scheduling(reordering) in the processor meand dispatch logic must be enhanced to look at group of instructions and dispatch them out of order called as out of order execution (ooo or oooE) In this dependencies between the instructions must be considered. processor keep the mapping of instructions in flight at anu moment and the physical registers they use called register renaming.
- approach 2 - compiler rearrange the code during compile time
 called static compile time instruction scheduling.

## The brainiac vs speed-demon debate

The out of order logic is costly while compiler can do the task of instruction scheduling well  enough without it.

The Brainiac designs are smart machines with lot of OOO hardware trying to squeeze instruction level parallelism out of code even if it costly. in constrast speed demon designs are simpler and smaller relying on compiler and willing to sacrifice a little bit of instruction level parallelism for the benefit that simplicity brings. historically speed demon tended to run at high clock speeds but today that's no longer the case because clock speed is limited mainly by power and thermal issues.

The clever engineering has reduced the power overhead of OOO execution considerably by late 1990s. unfortunately the effectiveness of OO execution in dynamically extracting additional instrcution level parallelism has been disappointing with only a relative small improvements seem


## The Power Wall & The ILP Wall
power increases linearly with clock frequency, it increases as the square of voltage, making for a kind of "triple whammy" at very high clock speeds (f*V*V).
Due to enormous increase in power and cooliong required for even smallest increased performance it is not possible to push clcok speed even fruther this is called power wall

normal programs just don't have a lot of fine-grained parallelism in them, due to a combination of load latencies, cache misses, branches and dependencies between instructions. This limit of available instruction-level parallelism is called the ILP wall.

# x86
with x86 Intel and AMd was able to remain competitive for 45 years  while Pentium superscalar x86 is state of the art it has complex and messy x86 instruction set complex addressing modes and minimal number of registers meant few instructions could be executed in parrallel due to potential dependencies. 

To compete with RISC in x86 instructions was dynamically decoded into simple RISC like micro instructions which can be executed by a fast RISC style register renaming OOO superscalar core. These Micro instructions are called μops (pronounced "micro-ops").most x86 instructions decode into 1,2,or 3 μops while complex instructions require a larger number

For these decoupled superscalar x86 processor register renaming is absolutely critical due to meager 8 registers of x86 arch in 32 bit mode (8=64 adds additional 8 register but still it's not a  lot) for providing more registers via renaming has mdoest effect exceptions of  advanced static instruction scheduling  not possible and use  a large register set to avoid memory accesses. 

Due to depcoupled  x86 instruction fetch and decode from internal RISC-like μop instruction dispatch and execution also makes defining the width of a modern x86 processor a bit tricky.because internally such processors often group or fuse miops into common pairs (load-and-add or compare-and-branch)for ease of tracking. One of the most interesting members of the RISC-style x86 group was the Transmeta Crusoe processor, which translated x86 instructions into an internal VLIW form, rather than internal superscalar, and used software to do the translation at runtime, much like a Java virtual machine or modern JavaScript JIT runtime.it i.e software translation did reduce system's performance compared to hardware translation. which resulte din lean chip and uses less power which is ideal for laptops 


## Threads -  SMT
Even with optimisation superscaled deep line average IPC is 2-3 instructions per cycle
Simultaneous multi-threading is a processor design technique which runs  independent instrcutons in thread level parallelism  like filling empty bubbles in the pipeline with useful instructions.From hardware pov only duplication in execution state like program counter, visble registers and memory mappings and so on little additional complexity for better squeeze in performance. It's suitable for application with highly cartiable code mixtures and threads don't constantly compete for same hardware resources.With all of those transistors available, it might also make sense to integrate other secondary functionality into the main CPU chip, such as I/O and networking (usually part of the motherboard chipset), dedicated video encoding/decoding hardware (usually part of the graphics system), or even an entire low-end GPU (graphics processing unit). This integration is particularly attractive in cases where a reduction in chip count, physical space or cost is more important than the performance advantage of more cores on the main CPU chip and separate, dedicated chips for those other purposes, making it ideal for phones, tablets and small, ultralight laptops. Such a heterogeneous design is called a system-on-chip, or SoC...

## Data Parallelism – SIMD Vector Instructions
In addition to Instruction level parallelism and thread level parallelism there is another one called Data parallelism the idea where on instruction apply to group of data values in parallel this is sometimes called SIMD parallelism (Single instruction multiple Data) also called vector processing ideal for scientific compution like super computers, imageing video memory wall isstill unsolved problem

## Caches & The Memory Hierarchy
modern processors solve memory wall via caching. A cache is a small but fast type of memory locates near the processor chip.it keeps copy of small pieces of main memory. typically there are small but fast primary L-1 cache on processor chip itself with larger L2 cache further but still on chip and possible even larger L3 cache . The combination of offchip external cahce (E -cache ) and main memory (RAM) forms memory hierarchy. also virtual memory(paging/swapping) provides illusion of infinte amount of main memory by moiving pages of RAM to and from storage.


Level	Size |	Latency | 	Physical | Location |
|----------|----------|----------| ------|
L1 cache	 |32 KB	|4 cycles |	inside each core |
L2 cache |	1 MB	|14 cycles	|beside each core|
L3 cache	|32 MB	|~49 cycles	|shared between all cores|
RAM	|4+ GB	|140+ cycles |	SDRAM DIMMs on motherboard|
Swap	| 100+ GB	|10,000+ | cycles	hard disk or SSD|

 modern primary caches achieve hit rates of around 90% for most software. So 90% of the time, accessing memory only takes a few cycles!

 Caches can achieve these seemingly amazing hit rates because of the way programs work. Most programs exhibit locality in both time and space, when a program accesses a piece of memory, there's a good chance it will need to re-access the same piece of memory in the near future (temporal locality), and there's also a good chance it will need to access other nearby memory in the future as well (spatial locality). Temporal locality is exploited by merely keeping recently accessed data in the cache. To take advantage of spatial locality, data is transferred from main memory up into the cache in blocks of a few dozen bytes at a time, called a cache line.

from hardware POV a cache works like a two column table one column memory address and other is the block of data values (eache line is whole block of data not single value). in reality the cache needs only store the necessary high end part of the address since lookupworks by using lowend part of the address to index the cache. when highest part called tag matches the tag stores in the tabel it's a hit and appropriate data is sent to core.common trick is to use virtual address for cache indexing but physical address for tags virtual to physical mapping can be performed in parrallel with cahce indexing.

## Cache Conflicts & Associativity
Ideally, a cache should keep the data that is most likely to be needed in the future. Since caches aren't psychic, a good approximation of this is to keep the most recently used data.
cache conflict is when cache allow data from any praticular address in memory to occupy one location. it can cause pathological worst case performamce.The nymber of places a piece of data can be stored in a cache is called associativity. means cache lookup works by association.each piece of data is simply mapped to address % size within the cache (direct mapped cache). A cache which allows data to occupy one of 2 locations based on its address is called 2-way set-associative. Similarly, a 4-way set-associative cache allows for 4 possible locations for any given piece of data, and an 8-way cache 8 possible locations. Set-associative caches work much like direct-mapped ones, except there are several tables, all indexed in parallel, and the tags from each table are compared to see whether there is a match for any one of them...Usually, set-associative caches are able to avoid the problems that occasionally occur with direct-mapped caches due to unfortunate cache conflicts.

The concept of caches also extends up into software systems. For example, the operating system uses main memory to cache the contents of the filesystem to speed up file I/O, and web browsers cache recently viewed pages, images and JavaScript files in case you revisit those sites. With respect to main memory and virtual memory (paging/swapping), it can be thought of as being a smart, fully associative cache, like the ideal cache mentioned \). After all, virtual memory is managed by the (hopefully) intelligent software of the OS kernel.


notes -> [https://www.lighterra.com/papers/modernmicroprocessors/](https://www.lighterra.com/papers/modernmicroprocessors/)
