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
with x86 Intel and AMd was able to remain competitive for 45 years


notes -> [https://www.lighterra.com/papers/modernmicroprocessors/](https://www.lighterra.com/papers/modernmicroprocessors/)
