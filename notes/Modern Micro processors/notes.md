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

If a pipelined processor executes the above instructions 

notes -> [https://www.lighterra.com/papers/modernmicroprocessors/](https://www.lighterra.com/papers/modernmicroprocessors/)
