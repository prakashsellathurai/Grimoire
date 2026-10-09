Memory safety has never been one of C Language's strong points. The Three sub-problem that needed to solve it

1. Type Safety
    Already have strong type system via header file yet tagless unions can create issues which can be improved by link time checker
2. Spatial Memory Safety
    Bound checking is partially solved compilers already doing array bound checking. the [counted_by](https://lwn.net/Articles/936728/) attribute can be for flexible array members
  ```c
  # define __counted_by(member) __attribute__((__element_count__(#member)))
```
3. Temporal Memory Safety
it's harder to avoid use-after-free bugs  Rust seems to be doing better on this Architectures like [CHERI](https://en.wikipedia.org/wiki/Capability_Hardware_Enhanced_RISC_Instructions) can help here is well. [Fil-C](https://lwn.net/Articles/1042938/) can find a lot of temporal-safety bugs.

[kernel recipes](https://uecker.codeberg.page/kernel-recipes.pdf)