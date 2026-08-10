
[Gnu Util Source](https://github.com/coreutils/coreutils/blob/master/src/tail.c)

## Simple example
```python
CHUNK_SIZE = 4096
def tail(path, n):
    """Return the last n lines of a file without loading it fully into memory."""
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        file_size = remaining = f.tell()
        buffer = b""
        newline_count = 0
 
        while remaining > 0 and newline_count <= n:
            read_size = min(CHUNK_SIZE, remaining)
            remaining -= read_size
            f.seek(remaining)
            chunk = f.read(read_size)
            buffer = chunk + buffer
            newline_count = buffer.count(b"\n")
 
        lines = buffer.splitlines()
        last_lines = lines[-n:] if n <= len(lines) else lines
        return [line.decode("utf-8", errors="replace") for line in last_lines]
```

## Sub problems

1. reading backwards through a file where one can read forward efficiently (no sys calls yet)
2. Doing the same thing on a pipe where can't seek at all - one pass
3. -f support file watching that may grow , shrink, gets renamed, deleted, or replaced across potentially many files using dumb polling or inotify for efficiency


## platform conditional

``sys/inotify.h`` only exists in linux or mac for windows polling based method can be used

## Core data structure
every tail cmd status of file is stored as
```c
struct File_spec {
  char *name;               // as given on the command line
  char const *prettyname;   // "standard input" if name is "-"
  struct timespec mtime; dev_t st_dev; ino_t st_ino; mode_t mode;  // last-seen identity
  off_t read_pos;           // how far we've read (regular files only)
  bool ignore, remote, tailable;
  int fd, errnum, blocking;
#if HAVE_INOTIFY
  int wd, parent_wd; idx_t basename_start;
#endif
  count_t n_unchanged_stats;
};
```

dev_t is Device ID of the storage device or filesystem containing the file and ino_t represents Inode number (or file serial number), which is a unique identifier for the file within that specific storage device.

`st_dev + st_ino` guaranteed to be global unique indentity for any file. it will be used to detect when a file is replaced or deleted

whether the file is healthy or not is provided by ``fd < 0`` or ``errnum == 0`` via valid_file_spec() function.

## Global states
The cli holds follwing states
 1. count_lines 
 2. follow_mode  (Follow_descriptor vs Follow_name)
 3. forever (-f) status
 4. .... rest of arguments like -n 

 - descriptor (default): keep the original file descriptor open. If the file is renamed or unlinked, you keep following the same underlying inode (like tail -f on a file being actively written).
 - name: keep re-resolving the path. If the path gets recreated

 ##  The static-file reading algorithms 
   1. dump_remainder() — the trivial base case 
        Loop `read()` into stack buffer, `write()` it out until EOF or `N_BYTES` satisfied
   2. file_lines() — backward line-counting on a seekable file
        1. seeks to `bufsize` - aligned position near EOF
        2. Reads a chunk (`BUFSIZ`, or `page_size` if the file size is a multiple of it this avoids a nasty edge case on `/proc`/`/sys` pseudo-files, which reject reads at certain seek offsets even though the seek itself "succeeds").
        3. Scans backward through the buffer using `memrchr()` to find `line_end` characters, decrementing `n_lines` for each one found.
        4. When `n_lines` hits the target, it's found the starting point: write everything after that newline, then `dump_remainder()` handles the rest of the file forward from there.
        5. If it runs out of newlines in a buffer, it seeks further back (`bufsize` further, accounting for what's already read) and reads another chunk, repeating.
   3. pipe_lines() / pipe_bytes() — the non-seekable case
      it builds linkedlist of fixed size buffers appending as data arrives and once it holds more than `n_lines`/`n_byetes` worth of data oldest buffer is discarded once the `read()`
      returns `EOF` walk the suruviveing buffer and prints the correct offset in one onward
   4. start_bytes() / start_lines() — the +N (skip-forward) case 
       just read and disacrd until N butes/lines skipped then flush what's left in the current buffer and hand off to ` dump_remainder()`

   ## watcher algorithm
   - Engine A: polling via `tail_forever()`
     loops forever compares mode, size and mtime against last seen values if chanhed print the new bytes and updates the states uses sleep interval
   - Engine B: `tail_forever_inotify()` event-driven, Linux only
     instead of using `sleep_interval` to check ebery file this registers kernel-level watched 
      - One watch per file (IN_MODIFY, plus IN_ATTRIB|IN_DELETE_SELF|IN_MOVE_SELF if Follow_name).
      - If `Follow_name`, also a watch on each file's parent directory (IN_CREATE|IN_DELETE|IN_MOVED_TO|...) — this is how it notices a rotated-away file's replacement being created, since you can't watch a path that doesn't exist yet.
    The event loop `poll()`s the inotify fd and process the batch of `struct inotify_event` records from a single read(). Handling branches on:
      - Event on a watched directory
      - IN_DELETE_SELF/IN_MOVE_SELF/IN_ATTRIB:
      - Plain data event: call check_fspec()
   recheck() -> the shared "is this still the same file?" logic
   Used by both engines when polling suspects rotation. It re-`open()`s the path, `fstat(`)`s it, and compares against the previous (`st_dev`, `st_ino`). Cases: symlink-replaced-a-regular-file (refuse to follow), became inaccessible, became an untailable type (directory etc.), moved to a remote filesystem, unchanged, or — the log-rotation case — !SAME_INODE(...), meaning a new file now exists at this path, so the old fd is closed and the new one is opened fresh via record_open_fd().

    ## overall flow
    1. parse args and set default
    2. sanity checks 
    3. allocate `File_spec` per input file.
    4. First pass:` tail_file()` each one,  this does the initial "print the last N units" using the static core algorithms, and if forever, leaves the `fd` open and populates the `File_spec` for later following.
    5. If -f was given: filter out FIFOs/pipes passed as  (`ignore_fifo_and_pipe`, per POSIX), decide whether stdout itself is a pipe worth monitoring for a dead reader, then choose inotify vs. polling based on the disqualifying conditions listed above, and hand off to the matching `tail_forever*`.
